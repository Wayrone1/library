from django.test import TestCase
from library_app.models import Genre, Book, Author
from library_app.config import CF_DEFAULT
from django.db.utils import DataError


def creation_tests(cls_model, normal: dict, failing: dict):
    class Tests(TestCase):
        def test_successful_creation(self):
            cls_model.objects.create(**normal)

        def test_failing_creation(self):
            with self.assertRaises(DataError):
                cls_model.objects.create(**failing)

    return Tests


normal_name = 'a' * CF_DEFAULT
long_name = 'a' * (CF_DEFAULT + 1)

GenreTests = creation_tests(Genre, {'name': normal_name}, {'name': long_name})
AuthorTests = creation_tests(Author, {'full_name': normal_name}, {'full_name': long_name})
BookTests = creation_tests(Book, {'title': normal_name}, {'title': long_name})
