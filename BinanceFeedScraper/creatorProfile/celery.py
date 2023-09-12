# creatorProfile/celery.py
from celery import Celery
from django.conf import settings 

# Create an instance of the Celery class with the name of the current module
app = Celery('creatorProfile')

# Load the Django settings module with the CELERY namespace
app.config_from_object(settings, namespace='CELERY')

# Autodiscover the tasks from the installed apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS) # Use a lambda function to get the installed apps dynamically

