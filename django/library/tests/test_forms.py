from django.test import TestCase
from library_app import forms
from library_app.config import LOCATIONS_COORDINATES
from random import sample
from string import ascii_letters


class WeatherLocationsException(Exception):
    def __init__(self, msg):
        super().__init__(f'WEATHER LOCATIONS ERROR: {msg}')


class WeatherFormTests(TestCase):
    def generate_random(self) -> str:
        return ''.join(sample(ascii_letters, 10))

    def test_successful(self):
        if not LOCATIONS_COORDINATES:
            raise WeatherLocationsException('locations are not provided by config')
        forms.WeatherForm(data={'location': list(LOCATIONS_COORDINATES.keys())[0]})

    def test_failing(self):
        if not LOCATIONS_COORDINATES:
            raise WeatherLocationsException('locations are not provided by config')
        location = self.generate_random()
        while location in LOCATIONS_COORDINATES.keys():
            location = self.generate_random()
        form = forms.WeatherForm(data={'location': location})
        desired_errors = [
            f'Выберите корректный вариант. {location} нет среди допустимых значений.',
            f'Select a valid choice. {location} is not one of the available choices.',
        ]
        for error in form.errors['location']:
            assert error in desired_errors
