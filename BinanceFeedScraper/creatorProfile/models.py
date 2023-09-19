from django.db import models
from dateutil.parser import parse


class Post(models.Model):
    # The title of the article, if any
    title = models.CharField(max_length=255, blank=True)
    # The summary of the article, if any
    summary = models.TextField(blank=True)
    # The URL of the article or the source website
    url = models.URLField(unique=True)
    # The datetime when the post was created
    created_at = models.DateTimeField(null=True, blank=True)
    # The datetime when the post was scraped
    scraped_at = models.DateTimeField(auto_now_add=True)
    # The tendency of the post, such as positive, negative, or neutral
    tendency = models.CharField(max_length=20, choices=[(
        "positive", "Positive"), ("negative", "Negative"), ("neutral", "Neutral")], default="neutral")
    # The main content of the article, if any
    content = models.TextField(blank=True)
    # The poster of the article or the source website, if any
    poster = models.CharField(max_length=100, blank=True)
    # The number of watches of the post
    watches = models.IntegerField(default=0)
    # The number of likes of the post
    likes = models.IntegerField(default=0)
    # The number of comments of the post
    comments = models.IntegerField(default=0)
    # The number of shares of the post
    shares = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # If the Post object is newly created, set its created_at attribute to the current datetime
        if not self.pk:
            self.created_at = models.DateTimeField(auto_now_add=True)

        # Call the superclass save method to save the object in the database
        super().save
