# BinanceFeedScraper 

## Description
This is a Django project that scrapes posts from a creator profile on Binance Feed and saves them in a database. It also provides an API endpoint to list and create posts.

## Requirements
- Python 3.10
- `requests` library
- `beautifulsoup4` library
- `lxml` library
- `Django 3.2.9`
- `Django REST Framework 3.12.4`
- `Celery 5.2.1`
- `Redis 6.2.6`
- `Selenium 4.1.0`
- `chromedriver-binary`
- `dateutil 2.8.2`
## Setup
1. Clone this repository.
2. Create and activate a virtual environment using `virtualenv` or `venv`.
3. Install the required libraries by running `pip install -r requirements.txt`.
4. Set the environment variable `CREATOR_PROFILE_URL` to the URL of the creator profile you want to scrape. 
5. Run `python manage.py migrate` to create the database tables.
6. Run the Django development server by executing `python manage.py runserver`.

## Usage
1. Start the Redis server in a terminal by running `redis-server`.
2. Start the Celery worker process in another terminal by running `celery -A creatorProfile worker -l info` (where `creatorProfile` is the name of Django app that contains the `celery.py` file).
3. Start the Celery beat process in another terminal by running `celery -A creatorProfile beat -l info` (if you have periodic tasks)
4. Start the Django development server in another terminal by running `python manage.py runserver`.
5. Open your browser and go to http://127.0.0.1:8000/creator/posts/ to see the list of posts scraped from the creator profile.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue.

