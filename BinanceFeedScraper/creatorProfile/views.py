from django.core.cache import cache
from django.conf import settings
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView
from .models import Post
from .serializers import CreatorInfoSerializer, PostSerializer
from celery import shared_task
from dateutil.parser import parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import os
from dotenv import load_dotenv
import requests
from lxml import html

# Load the environment variables from .env file
load_dotenv()

# Set up the logger
logging.basicConfig(filename='logs/main.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

@api_view(['GET'])
def creator_details(request):
    try:
        # Check if the data is in the cache
        data = cache.get('creator_info')

        if data is None:
            # Fetch the web page using environment variable for the URL
            page = requests.get(os.getenv('CREATOR_PROFILE_URL'))
            tree = html.fromstring(page.content)

            # Extract the information using xpath
            avatar_name = tree.xpath("//div[contains(@class, 'profile-contaniner')]//div[contains(@class, 'avatar-name-container')]//div[contains(@class, 'nick')]/text()")
            avatar_image = tree.xpath("//div[@class='avatar-box']/img/@data-src")
            followers_count = tree.xpath("//div[contains(@class, 'profile-contaniner')]//div[contains(@class, 'kol-info-bottom-column')]//div//div/text()")
            liked_count = tree.xpath("//div[contains(@class, 'profile-contaniner')]//div[contains(@class, 'kol-info-bottom-column')]//div//div/text()")
            shared_count = tree.xpath("//div[contains(@class, 'profile-contaniner')]//div[contains(@class, 'kol-info-bottom-column')]//div//div/text()")
            bio_text = tree.xpath("//div[contains(@class,'profile-contaniner')]//div/text()")
            last_post = tree.xpath("(//div[@class='create-time'])/text()")

            # Create a serializer instance with the extracted data
            data = {
                'avatar_name': avatar_name,
                'avatar_image': avatar_image,
                'followers_count': followers_count,
                'liked_count': liked_count,
                'shared_count': shared_count,
                'bio_text': bio_text,
                'last_post': last_post,
            }
            serializer = CreatorInfoSerializer(data=data)

            # Validate and cache the serialized data
            if serializer.is_valid():
                data = serializer.data
                cache.set('creator_info', data, timeout=settings.CACHE_TTL)
            else:
                return Response(serializer.errors, status=400)

        # Return the cached data
        return Response(data)
    except Exception as e:
        # Log the exception and return an error message
        logging.error(e)
        return Response({'message': 'Something went wrong. Please try again later.'}, status=500)

@shared_task
def scrape_posts():
    try:
        # Get the profile URL from the environment variable
        url = os.environ.get("CREATOR_PROFILE_URL")

        # Create a driver instance and open the URL
        driver = webdriver.Chrome()
        driver.get(url)

        # Wait for the posts to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "css-1x9zltl")))

        # Initialize an empty list to store the posts elements
        posts = []

        # Initialize a variable to store the number of posts
        num_posts = 0

        # Loop until there are no more posts to load
        while True:
            # Find all the posts elements on the page
            posts = driver.find_elements_by_class_name("css-1x9zltl")

            # Get the current number of posts
            current_posts = len(posts)

            # Check if there are new posts loaded
            if current_posts > num_posts:
                # Update the number of posts
                num_posts = current_posts

                # Scroll to the bottom of the page
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # Wait for new posts to load or timeout
                try:
                    wait.until(lambda driver: len(driver.find_elements_by_class_name("css-1x9zltl")) > num_posts)
                except:
                    # No more posts loaded, break the loop
                    break
            else:
                # No more posts loaded, break the loop
                break

        # Get or create a Post object for each post element and save it in the database
        for post in posts:
            # Get the title, summary, and URL of the post
            title = post.find_element_by_class_name("css-1kx3y31").text
            summary = post.find_element_by_class_name("css-vurnku").text
            post_url = post.find_element_by_tag_name("a").get_attribute("href")

            # Get or create a Post object with the same title and URL as the post element
            post_obj, created = Post.objects.get_or_create(title=title, url=post_url)

            # If the Post object is newly created, set its summary and created_at attributes and save it
            if created:
                post_obj.summary = summary

                # Find the creation time element by its class name and get its text content
                create_time = post.find_element_by_class_name("create-time").text

                # Parse the creation time string into a datetime object using dateutil.parser.parse
                create_time = parse(create_time)

                # Set the created_at attribute of the Post object to the datetime object
                post_obj.created_at = create_time
                post_obj.save()

        # Close the driver
        driver.quit()

    except Exception as e:
        # Log the exception
        logging.error(e)

class PostListCreateAPIView(ListCreateAPIView):
    # Specify the queryset and serializer class for this view
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @cache_page(settings.CACHE_TTL)
    def get(self, request, *args, **kwargs):
        try:
            # Call the Celery task to scrape the posts asynchronously
            scrape_posts.delay()

            # Get all the Post objects from the database and order them by creation date (newest first)
            posts = Post.objects.all().order_by("-created_at")

            # Serialize the posts data
            serializer = self.get_serializer(posts, many=True)

            # Return a JSON response with the serialized data
            return Response(serializer.data)
        except Exception as e:
            # Log the exception and return an error message
            logging.error(e)
            return Response({'message': 'Something went wrong. Please try again later.'}, status=500)

    def post(self, request, *args, **kwargs):
        # Get the request data
        data = request.data

        # Validate and serialize the data
        serializer = self.get_serializer(data=data)

        # Save the serialized data as a Post object in the database
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return a JSON response with the serialized data and a status code of 201 (created)
        return Response(serializer.data, status=201)


def post_detail():
    pass
