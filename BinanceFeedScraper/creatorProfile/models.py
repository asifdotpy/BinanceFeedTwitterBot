from django.db import models
from dateutil.parser import parse

class Post(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    url = models.URLField(unique=True)
    created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # If the Post object is newly created, set its created_at attribute to the current datetime
        if not self.pk:
            self.created_at = models.DateTimeField(auto_now_add=True)

        # Call the superclass save method to save the object in the database
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
