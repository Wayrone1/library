from django.test import TestCase
from library_app.models import Genre, Author, Book
from django.urls import reverse
from rest_framework.status import HTTP_200_OK as OK
from django.contrib.auth.models import User
from django.test.client import Client
from library_app.config import PAGINATOR_THRESHOLD
from string import ascii_letters as letters


def test_view(url, page_name, template, cls_model=None, attrs=None):
    class ViewTest(TestCase):
        def setUp(self):
            self.client = Client()
            username = letters[:10]
            password = letters[:10]
            self.user = User.objects.create_user(username=username, email='a@a.com', password=password)
            self.client.login(username=username, password=password)
            self.extra = 1
            if cls_model:
                for _ in range(PAGINATOR_THRESHOLD + self.extra):
                    cls_model.objects.create(**attrs)

        def test_exists_by_url(self):
            self.assertEqual(self.client.get(url).status_code, OK)

        def test_exists_by_name(self):
            self.assertEqual(self.client.get(reverse(page_name)).status_code, OK)

        def test_view_template(self):
            response = self.client.get(url)
            self.assertEqual(response.status_code, OK)
            self.assertTemplateUsed(response, template)

        def test_pagination(self):
            if cls_model:
                resp_get = self.client.get(reverse(page_name))
                self.assertEqual(resp_get.status_code, OK)
                self.assertTrue('is_paginated' in resp_get.context)
                self.assertEqual(resp_get.context.get('is_paginated'), True)

                # testing the number of model objects on first page
                resp_first_page = self.client.get(reverse(page_name), {'query': '', 'page': 1})
                self.assertEqual(len(resp_first_page.context.get(f'{page_name}_list')), PAGINATOR_THRESHOLD)

                # testing the number of model objects on second page
                resp_second_page = self.client.get(reverse(page_name), {'query': '', 'page': 2})
                self.assertEqual(len(resp_second_page.context.get(f'{page_name}_list')), self.extra)

    return ViewTest


genre_attrs = {'name': 'genre'}
GenreListViewTest = test_view('/genres/', 'genres', 'catalog/genres.html', Genre, genre_attrs)
author_attrs = {'full_name': 'Fool Name'}
AuthorListViewTest = test_view('/authors/', 'authors', 'catalog/authors.html', Author, author_attrs)
book_attrs = {'title': 'Title'}
BookListViewTest = test_view('/books/', 'books', 'catalog/books.html', Book, book_attrs)
HomePageTest = test_view('', 'homepage', 'index.html')
WeatherPageTest = test_view('/weather/', 'weather', 'pages/weather.html')
