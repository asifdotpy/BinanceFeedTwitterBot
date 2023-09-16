from django.core.cache import cache
from django.conf import settings
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework_extensions.cache.decorators import cache_response
from .models import Post
from .serializers import CreatorInfoSerializer, PostSerializer
from celery import shared_task
from dateutil.parser import parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import logging
import os
from dotenv import load_dotenv
import requests
from lxml import html

# Load the environment variables from .env file
load_dotenv()

# Get the absolute path of the directory containing the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the relative path from the script directory to the project directory
project_rel_path = '..'

# Join the script directory with the relative path to get the absolute path to the project directory
project_dir = os.path.join(script_dir, project_rel_path)

# Define the relative path from the project directory to the log directory
log_rel_path = 'logs'

# Join the project directory with the relative path to get the absolute path to the log directory
log_dir = os.path.join(project_dir, log_rel_path)

# Create the log directory if it doesn't exist
os.makedirs(log_dir, exist_ok=True)

# Define the path to the main log file
log_file = os.path.join(log_dir, 'main.log')

# Set up the logger
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


@api_view(['GET'])
def creator_details(request):
    try:
        # Check if the data is in the cache
        data = cache.get('creator_info')

        if data is None:
            # Fetch the web page using environment variable for the URL
            profile_url = os.getenv('CREATOR_PROFILE_URL')
            # Add a try-except block to handle invalid URL and timeout exceptions
            try:
                response = requests.get(profile_url)
            except requests.exceptions.InvalidURL as err:
                # Log the invalid URL and raise the exception again
                logging.error(f"Invalid URL: {err.request.url}")
                raise
            except requests.exceptions.Timeout as err:
                # Log the timeout error and raise the exception again
                logging.error(f"Timeout error: {err.request.url}")
                raise

            # Handle common HTTP errors by raising appropriate exceptions and logging error messages
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as err:
                # Log the status code, the reason, and the URL of the request
                logging.error(
                    f"HTTP error occurred: {err.response.status_code} {err.response.reason} {err.request.url}")
                # Raise the exception again to be handled by the outer except block
                raise

            # Parse the response content as HTML
            tree = html.fromstring(response.content)

            # Extract the information using xpath
            avatar_name = tree.xpath(
                "//div[contains(@class, 'profile-contaniner')]//div[contains(@class, 'avatar-name-container')]//div[contains(@class, 'nick')]/text()")[0]
            # avatar_image = tree.xpath(
            #    "(//div[@class='avatar-box click-able css-4cffwv']/img[@src])[1]")
            followers_count = int(tree.xpath(
                "(//div[contains(@class, 'profile-contaniner')]//div[contains(@class, 'kol-info-bottom-column')]/div)[1]/div[1]/text()")[0])
            liked_count = int(tree.xpath(
                "(//div[contains(@class, 'profile-contaniner')]//div[contains(@class, 'kol-info-bottom-column')]/div)[2]/div[1]/text()")[0])
            shared_count = int(tree.xpath(
                "(//div[contains(@class, 'profile-contaniner')]//div[contains(@class, 'kol-info-bottom-column')]/div)[3]/div[1]/text()")[0])
            bio_text = tree.xpath(
                "//div[contains(@class,'profile-contaniner')]/div/div[3]/text()")[0]
            last_post = tree.xpath(
                "((//div[@class='create-time']))[1]/text()")[0]
            # Extract the Binance ID from the profile URL
            binance_id = profile_url.split('/')[-1]

            # Create a serializer instance with the extracted data
            data = {
                'binance_id': binance_id,
                'avatar_name': avatar_name,
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
            else:
                data = serializer.initial_data
                print(data)
                print(serializer.errors)
            cache.set('creator_info', data, timeout=settings.CACHE_TTL)
        # Return the cached data
        return Response(data)
    except Exception as e:
        # Log the exception and return an error message
        logging.error(e)
        return Response({'message': 'Something went wrong. Please try again later.'}, status=500)


@shared_task
def scrape_posts():
    # Get the profile URL from the environment variable
    url = os.environ.get("CREATOR_PROFILE_URL")

    # Check if the URL is valid
    if not url:
        logging.error("No profile URL found in environment variable")
        return

    # Create a driver instance
    try:
        options = Options()
        options.add_argument("--no-sandbox")  # Bypass OS security model
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--disable-gpu")  # Disable GPU acceleration
        # Overcome limited resource problems
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=ChromeService(
            ChromeDriverManager().install(), options=options))

    except Exception as e:
        logging.error("Failed to create driver instance", exc_info=e)
        return

    # Open the URL
    try:
        driver.get(url)
    except Exception as e:
        logging.error("Failed to open profile URL", exc_info=e)
        driver.quit()
        return

    # Wait for the posts to load
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "css-1x9zltl")))
    except Exception as e:
        logging.error("Failed to wait for posts elements", exc_info=e)
        driver.quit()
        return

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
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")

            # Wait for new posts to load or timeout
            try:
                wait.until(lambda driver: len(
                    driver.find_elements_by_class_name("css-1x9zltl")) > num_posts)
            except Exception as e:
                logging.warning(
                    "No more posts loaded or timed out", exc_info=e)
                break
        else:
            # No more posts loaded, break the loop
            break

    # Get or create a Post object for each post element and save it in the database
    for post in posts:
        try:
            # Get the title, summary, and URL of the post
            title = post.find_element_by_class_name("css-1kx3y31").text
            summary = post.find_element_by_class_name("css-vurnku").text
            post_url = post.find_element_by_tag_name("a").get_attribute("href")

            # Get or create a Post object with the same title and URL as the post element
            post_obj, created = Post.objects.get_or_create(
                title=title, url=post_url)

            # If the Post object is newly created, set its summary and created_at attributes and save it
            if created:
                post_obj.summary = summary

                # Find the creation time element by its class name and get its text content
                create_time = post.find_element_by_class_name(
                    "create-time").text

                # Parse the creation time string into a datetime object using dateutil.parser.parse
                create_time = parse(create_time)

                # Set the created_at attribute of the Post object to the datetime object
                post_obj.created_at = create_time
                post_obj.save()
        except Exception as e:
            logging.error("Failed to get or create Post object", exc_info=e)

    # Close the driver
    driver.quit()


def my_cache_key(self, view_instance, view_method,
                 request, args, kwargs):
    return '{user}-{params}'.format(
        user=request.user.id,
        params=request.query_params.urlencode()
    )


class PostListCreateAPIView(ListCreateAPIView):
    # Specify the queryset and serializer class for this view
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    # Use the cache_response decorator with a custom key_func argument
    @cache_response(timeout=settings.CACHE_TTL, key_func='my_cache_key')
    def get(self, request, *args, **kwargs):
        try:
            # Call the Celery task to scrape the posts synchronously
            scrape_posts()

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

    def my_cache_key(self, view_instance, view_method,
                     request, args, kwargs):
        return '{user}-{params}'.format(
            user=request.user.id,
            params=request.query_params.urlencode()
        )


# write post details


@api_view(['GET'])
def post_details(request, pk):
    pass
