from django.db import models
from uuid import uuid4
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from . import config
from django.conf.global_settings import AUTH_USER_MODEL


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)

    class Meta:
        abstract = True


class CreatedMixin(models.Model):
    created = models.DateTimeField(_('created'), default=datetime.now, blank=True, null=False)

    class Meta:
        abstract = True


class ModifiedMixin(models.Model):
    modified = models.DateTimeField(_('modified'), default=datetime.now, blank=True, null=False)

    class Meta:
        abstract = True


class Author(UUIDMixin, CreatedMixin, ModifiedMixin):
    full_name = models.CharField(_('full name'), max_length=config.CF_DEFAULT)
    books = models.ManyToManyField('Book', verbose_name=_('books'), through='BookAuthor')

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = '"library"."author"'
        verbose_name = _('author')
        verbose_name_plural = _('authors')


def positive_int(num: int):
    if num <= 0:
        raise ValidationError(
            f'Value {num} is less or equal zero',
            params={'value': num},
        )


def year_validator(year: int):
    current_year = datetime.now().year
    if year > current_year:
        raise ValidationError(
            f'The year field must be less or equal {current_year}',
            params={'year': year},
        )


book_types = (
    ('book', _('book')),
    ('journal', _('journal')),
)


class Book(UUIDMixin, CreatedMixin, ModifiedMixin):
    title = models.CharField(_('title'), max_length=config.CF_DEFAULT)
    description = models.TextField(_('description'), blank=True, null=True)
    volume = models.IntegerField(_('volume'), blank=True, null=True, validators=[positive_int])
    age_limit = models.IntegerField(_('age limit'), blank=True, null=True, validators=[positive_int])
    year = models.IntegerField(_('year'), blank=True, null=True, validators=[year_validator])
    type = models.CharField(_('type'), max_length=config.CF_DEFAULT, choices=book_types, blank=False, null=False)
    authors = models.ManyToManyField(Author, verbose_name=_('authors'), through='BookAuthor')
    genres = models.ManyToManyField('Genre', verbose_name=_('genres'), through='BookGenre')
    price = models.DecimalField(
        verbose_name=_('price'),
        max_digits=config.DECIMAL_MAX_DIGITS,
        decimal_places=config.DECIMAL_PLACES,
        default=0,
        blank=False,
        null=False,
    )

    def __str__(self):
        return f'{self.title}, {self.type}, {self.year}'

    class Meta:
        db_table = '"library"."book"'
        verbose_name = _('book')
        verbose_name_plural = _('books')


class BookAuthor(UUIDMixin, CreatedMixin):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta:
        db_table = '"library"."book_author"'
        unique_together = (('book', 'author'),)


class Genre(UUIDMixin, CreatedMixin, ModifiedMixin):
    name = models.CharField(_('name'), max_length=config.CF_DEFAULT)
    description = models.TextField(_('description'), blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = '"library"."genre"'
        verbose_name = _('genre')
        verbose_name_plural = _('genres')


class BookGenre(UUIDMixin, CreatedMixin):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        db_table = '"library"."book_genre"'
        unique_together = (('book', 'genre'),)


class Client(CreatedMixin, ModifiedMixin):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    money = models.DecimalField(
        max_digits=config.DECIMAL_MAX_DIGITS,
        decimal_places=config.DECIMAL_PLACES,
        default=0,
    )
    books = models.ManyToManyField(Book, through='BookClient')

    class Meta:
        db_table = '"library"."client"'
        verbose_name = _('client')
        verbose_name_plural = _('clients')


class BookClient(UUIDMixin, CreatedMixin):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=False, null=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        db_table = '"library"."book_client"'
        unique_together = (('book', 'client'),)
