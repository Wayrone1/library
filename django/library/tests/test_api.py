from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.test.client import Client
from rest_framework.test import APIClient
from library_app.models import Genre, Book, Author
import json


class ViewSetsTests(TestCase):
    id_query = '?id='
    pages = (
        (Genre, '/rest/Genre/', {'name': 'genre'}, {'description': 'abcdefghiklmnop'}),
        (Book, '/rest/Book/', {'title': 'book', 'type': 'book'}, {'description': 'abcdefghiklmnop'}),
        (Author, '/rest/Author/', {'full_name': 'name'}, {'full_name': 'new_name'}),
    )

    def setUp(self):
        self.client = Client()
        self.creds_superuser = {'username': 'super', 'password': 'super'}
        self.creds_user = {'username': 'default', 'password': 'default'}
        self.superuser = User.objects.create_user(is_superuser=True, **self.creds_superuser)
        self.user = User.objects.create_user(**self.creds_user)
        self.token = Token.objects.create(user=self.superuser)

    def test_get(self):
        # logging in with superuser creds
        self.client.login(**self.creds_user)
        # GET
        for _, url, _, _ in self.pages:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # logging out
        self.client.logout()

    def manage(self, auth_token=False):
        for cls_model, url, attrs, to_change in self.pages:
            # POST
            resp_post = self.client.post(url, data=attrs)
            self.assertEqual(resp_post.status_code, status.HTTP_201_CREATED)
            created_id = cls_model.objects.get(**attrs).id
            # PUT
            if not auth_token:
                resp_put = self.client.put(
                    f'{url}{self.id_query}{created_id}',
                    data=json.dumps(to_change),
                )
                self.assertEqual(resp_put.status_code, status.HTTP_200_OK)
                attr, obj_value = list(to_change.items())[0]
                self.assertEqual(getattr(cls_model.objects.get(id=created_id), attr), obj_value)
            # DELETE EXISTING
            resp_delete = self.client.delete(f'{url}{self.id_query}{created_id}')
            self.assertEqual(resp_delete.status_code, status.HTTP_204_NO_CONTENT)
            # DELETE NONEXISTENT
            repeating_delete = self.client.delete(f'{url}{self.id_query}{created_id}')
            self.assertEqual(repeating_delete.status_code, status.HTTP_404_NOT_FOUND)

    def test_manage_superuser(self):
        # logging in with superuser creds
        self.client.login(**self.creds_superuser)

        self.manage()

        # logging out
        self.client.logout()

    def test_manage_user(self):
        # logging in with superuser creds
        self.client.login(**self.creds_user)
        for cls_model, url, attrs, to_change in self.pages:
            # POST
            resp_post = self.client.post(url, data=attrs)
            self.assertEqual(resp_post.status_code, status.HTTP_403_FORBIDDEN)
            # PUT
            created = cls_model.objects.create(**attrs)
            resp_put = self.client.put(
                f'{url}{self.id_query}{created.id}',
                data=json.dumps(to_change),
            )
            print(f'RESP PUT CONTENT: {resp_put.content}')
            self.assertEqual(resp_put.status_code, status.HTTP_403_FORBIDDEN)
            # DELETE EXISTING
            resp_delete = self.client.delete(f'{url}{self.id_query}{created.id}')
            self.assertEqual(resp_delete.status_code, status.HTTP_403_FORBIDDEN)
            # clean up
            created.delete()
        # logging out
        self.client.logout()

    def test_manage_token(self):
        # creating rest_framework APIClient instead of django test Client
        # because it can be forcefully authenticated with token auth
        self.client = APIClient()

        self.client.force_authenticate(user=self.superuser, token=self.token)
        self.manage(auth_token=True)
