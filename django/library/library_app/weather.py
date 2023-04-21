from requests import get
from .config import YANDEX_API_HEADER, YANDEX_API_URL, YANDEX_KEY, LOCATIONS_COORDINATES


def get_weather(location: str):
    return get(
        YANDEX_API_URL,
        params=LOCATIONS_COORDINATES.get(location),
        headers={YANDEX_API_HEADER: YANDEX_KEY},
    )
