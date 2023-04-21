from django.shortcuts import render
from .models import Book, Genre, Author, Client
from django.views.generic import ListView
from django.core.paginator import Paginator
from rest_framework import viewsets, permissions, status as status_codes, parsers, decorators
from .serializers import BookSerializer, AuthorSerializer, GenreSerializer
from rest_framework.response import Response
from . import config
from .forms import WeatherForm, AddFundsForm, RegistrationForm
from .weather import get_weather
from django.contrib.auth import mixins, decorators as auth_decorators
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse


def register(request):
    form_errors = None
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Client.objects.create(user=user)
            return HttpResponseRedirect(reverse('profile'))
        form_errors = form.errors
    return render(
        request,
        config.TEMPLATE_REGISTER,
        context={
            'form': RegistrationForm(),
            'form_errors': form_errors,
        },
    )


@auth_decorators.login_required
def read_page(request):
    context = {}
    client = Client.objects.get(user=request.user)
    book_id = request.GET.get('id')
    try:
        context['book'] = Book.objects.get(id=book_id)
    except Exception:
        context['book'] = None
    try:
        context['user_access'] = bool(client.books.get(id=book_id))
    except Exception:
        context['user_access'] = False

    return render(
        request,
        config.TEMPLATE_READ,
        context=context,
    )


@auth_decorators.login_required
def purchase_page(request):
    client = Client.objects.get(user=request.user)
    book_id = request.GET.get('id', '')
    try:
        book = Book.objects.get(id=book_id)
    except Exception:
        book = None
    else:
        if request.method == 'POST' and client.money >= book.price:
            with transaction.atomic():
                client.money -= book.price
                client.books.add(book)
                client.save()
            url = reverse('book')
            return HttpResponseRedirect(f'{url}?id={book_id}')

    return render(
        request,
        template_name=config.TEMPLATE_PURCHASE,
        context={
            'book': book,
            'funds': client.money,
            'enough_money': client.money - book.price >= 0,
        },
    )


@transaction.atomic
@auth_decorators.login_required
def profile_page(request):
    user = request.user
    client = Client.objects.get(user=user)
    form_errors = []

    if request.method == 'POST':
        form = AddFundsForm(request.POST)

        if form.is_valid():
            funds_to_add = form.cleaned_data.get('money')
            if funds_to_add > 0:
                client.money += funds_to_add
                try:
                    client.save()
                except Exception as error:
                    form_errors.append(str(error))
                else:
                    return HttpResponseRedirect(reverse('profile'))
        else:
            form_errors.extend(form.errors.get('money'))
    user_data = {
        'username': user.username,
        'first name': user.first_name,
        'last name': user.last_name,
        'email': user.email,
        'money': client.money,
    }

    return render(
        request,
        config.TEMPLATE_PROFILE,
        context={
            'form': AddFundsForm(),
            'user_data': user_data,
            'form_errors': '; '.join(form_errors),
            'books': [book.title for book in client.books.all()],
        },
    )


@decorators.api_view(['GET'])
def weather_rest(request):
    location = request.GET.get('location')
    locations = config.LOCATIONS_COORDINATES.keys()
    if not location or location not in locations:
        return Response(
            f'Wrong location value in query, available locations are: {locations}',
            status=status_codes.HTTP_400_BAD_REQUEST,
        )
    response = get_weather(location)
    if response and response.status_code == status_codes.HTTP_200_OK:
        return Response(response.json().get('fact'), status=status_codes.HTTP_200_OK)
    return Response(
        'Foreign weather API did not repond properly',
        status=status_codes.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@auth_decorators.login_required
def weather_page(request):
    location = request.GET.get('location')
    weather_data = {}
    if location:
        response = get_weather(location)
        if response and response.status_code == status_codes.HTTP_200_OK:
            weather_data = response.json().get('fact')
    return render(
        request,
        config.TEMPLATE_WEATHER,
        context={
            'form': WeatherForm(),
            'weather_data': weather_data,
        },
    )


def custom_main(request):
    return render(
        request,
        config.TEMPLATE_MAIN,
        context={
            'books': Book.objects.all().count(),
            'genres': Genre.objects.all().count(),
            'authors': Author.objects.all().count(),
        },
    )


def catalog_view(cls_model, context_name, template):
    class CustomListView(mixins.LoginRequiredMixin, ListView):
        model = cls_model
        template_name = template
        paginate_by = config.PAGINATOR_THRESHOLD
        context_object_name = context_name

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            instances = cls_model.objects.all()
            paginator = Paginator(instances, config.PAGINATOR_THRESHOLD)
            page = self.request.GET.get('page')
            page_obj = paginator.get_page(page)
            context[f'{context_name}_list'] = page_obj
            return context

    return CustomListView


def entity_view(cls_model, name, template):
    @auth_decorators.login_required
    def view(request):
        target_id = request.GET.get('id', '')
        context = {name: cls_model.objects.get(id=target_id)}
        if cls_model is Book:
            client = Client.objects.get(user=request.user)
            try:
                context['client_has_book'] = bool(client.books.get(id=target_id))
            except Exception:
                context['client_has_book'] = False

        return render(
            request,
            template,
            context=context,
        )
    return view


BookListView = catalog_view(Book, 'books', config.BOOKS_CATALOG)
AuthorListView = catalog_view(Author, 'authors', config.AUTHORS_CATALOG)
GenreListView = catalog_view(Genre, 'genres', config.GENRES_CATALOG)

book_view = entity_view(Book, 'book', config.BOOK_ENTITY)
genre_view = entity_view(Genre, 'genre', config.GENRE_ENTITY)
author_view = entity_view(Author, 'author', config.AUTHOR_ENTITY)


class Permission(permissions.BasePermission):
    safe_methods = ('GET', 'HEAD', 'OPTIONS', 'PATCH')
    unsafe_methods = ('POST', 'PUT', 'DELETE')

    def has_permission(self, request, _):
        if request.method in self.safe_methods:
            return bool(request.user and request.user.is_authenticated)
        elif request.method in self.unsafe_methods:
            return bool(request.user and request.user.is_superuser)
        return False


def query_from_request(cls_serializer, request) -> dict:
    query = {}
    for field in cls_serializer.Meta.fields:
        obj_value = request.GET.get(field, '')
        if obj_value:
            query[field] = obj_value
    return query


def create_viewset(cls_model, serializer, order_field):
    class CustomViewSet(viewsets.ModelViewSet):
        queryset = cls_model.objects.all()
        serializer_class = serializer
        permission_classes = [Permission]

        def get_queryset(self):
            query = query_from_request(serializer, self.request)
            queryset = cls_model.objects.filter(**query) if query else cls_model.objects.all()
            return queryset.order_by(order_field)

        def delete(self, request):
            def response_from_objects(num):
                if not num:
                    message = f'DELETE for model {cls_model.__name__}: query did not match any objects'
                    return Response(message, status=status_codes.HTTP_404_NOT_FOUND)
                status = status_codes.HTTP_204_NO_CONTENT if num == 1 else status_codes.HTTP_200_OK
                return Response(f'DELETED {num} instances of {cls_model.__name__}', status=status)

            query = query_from_request(serializer, request)
            if query:
                instances = cls_model.objects.all().filter(**query)
                num_objects = len(instances)
                try:
                    instances.delete()
                except Exception as error:
                    return Response(error, status=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)
                return response_from_objects(num_objects)
            return Response('DELETE has got no query', status=status_codes.HTTP_400_BAD_REQUEST)

        def put(self, request):
            # gets id from query and updates instance with this ID, creates new if doesnt find any.
            def serialize(target):
                attrs = parsers.JSONParser().parse(request)
                model_name = cls_model.__name__
                if target:
                    serialized = serializer(target, data=attrs, partial=True)
                    status = status_codes.HTTP_200_OK
                    body = f'PUT has updated {model_name} instance'
                else:
                    serialized = serializer(data=attrs, partial=True)
                    status = status_codes.HTTP_201_CREATED
                    body = f'PUT has created new {model_name} instance'
                if not serialized.is_valid():
                    return (
                        f'PUT could not serialize query {query} into {model_name}',
                        status_codes.HTTP_400_BAD_REQUEST,
                    )
                try:
                    model_obj = serialized.save()
                except Exception as error:
                    return error, status_codes.HTTP_500_INTERNAL_SERVER_ERROR
                body = f'{body} with id={model_obj.id}'
                return body, status

            query = query_from_request(serializer, request)
            target_id = query.get('id', '')
            if not target_id:
                return Response('PUT has got no id', status=status_codes.HTTP_400_BAD_REQUEST)
            try:
                target_object = cls_model.objects.get(id=target_id)
            except Exception:
                target_object = None
            message, status = serialize(target_object)
            return Response(message, status=status)

    return CustomViewSet


BookViewSet = create_viewset(Book, BookSerializer, 'title')
AuthorViewSet = create_viewset(Author, AuthorSerializer, 'full_name')
GenreViewSet = create_viewset(Genre, GenreSerializer, 'name')
