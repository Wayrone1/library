from dotenv import load_dotenv
from os import getenv

load_dotenv()

PAGINATOR_THRESHOLD = 20
TEMPLATE_WEATHER = 'pages/weather.html'
TEMPLATE_PROFILE = 'pages/profile.html'
TEMPLATE_PURCHASE = 'pages/purchase.html'
TEMPLATE_READ = 'pages/read.html'
TEMPLATE_REGISTER = 'registration/register.html'
TEMPLATE_MAIN = 'index.html'

ENTITIES = 'entities'
BOOK_ENTITY = f'{ENTITIES}/book.html'
AUTHOR_ENTITY = f'{ENTITIES}/author.html'
GENRE_ENTITY = f'{ENTITIES}/genre.html'

CATALOG = 'catalog'
BOOKS_CATALOG = f'{CATALOG}/books.html'
AUTHORS_CATALOG = f'{CATALOG}/authors.html'
GENRES_CATALOG = f'{CATALOG}/genres.html'

# weather consts
COLLEGE_LOCATION = {'lat': 43.403438, 'lon': 39.981544}
SOCHI_LOCATION = {'lat': 43.713351, 'lon': 39.580041}
POLYANA_LOCATION = {'lat': 43.661294, 'lon': 40.268936}
LOCATIONS_COORDINATES = {
    'college': COLLEGE_LOCATION,
    'sochi': SOCHI_LOCATION,
    'polyana': POLYANA_LOCATION
}
YANDEX_API_URL = 'https://api.weather.yandex.ru/v2/informers'
YANDEX_API_HEADER = 'X-Yandex-API-Key'
LOCATIONS_NAMES = [(key, key) for key in LOCATIONS_COORDINATES.keys()]
YANDEX_KEY = getenv('YANDEX_KEY')

CF_DEFAULT = 40
DECIMAL_MAX_DIGITS = 10
DECIMAL_PLACES = 2
EMAIL_LENGTH = 128
