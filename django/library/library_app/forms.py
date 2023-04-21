from django.forms import ChoiceField, Form, DecimalField, CharField, EmailField
from .config import LOCATIONS_NAMES, DECIMAL_MAX_DIGITS, DECIMAL_PLACES, CF_DEFAULT, EMAIL_LENGTH
from django.contrib.auth import forms as auth_forms, models as auth_models


class WeatherForm(Form):
    location = ChoiceField(label='location', choices=LOCATIONS_NAMES)


class AddFundsForm(Form):
    money = DecimalField(
        label='Amount',
        max_digits=DECIMAL_MAX_DIGITS,
        decimal_places=DECIMAL_PLACES,
    )


class RegistrationForm(auth_forms.UserCreationForm):
    first_name = CharField(max_length=CF_DEFAULT, required=True)
    last_name = CharField(max_length=CF_DEFAULT, required=True)
    email = EmailField(max_length=EMAIL_LENGTH, required=True)

    class Meta:
        model = auth_models.User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2']
