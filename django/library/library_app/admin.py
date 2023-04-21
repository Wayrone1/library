from django.contrib import admin
from .models import Book, Genre, Author, BookAuthor, BookGenre, Client, BookClient
from datetime import datetime


DECADE = 10


class BookAuthorInline(admin.TabularInline):
    model = BookAuthor
    extra = 1


class BookGenreInline(admin.TabularInline):
    model = BookGenre
    extra = 1


class RecencyBookFilter(admin.SimpleListFilter):
    title = 'recency'
    parameter_name = 'recency'

    def lookups(self, *_):
        return (
            ('10yo', 'Written in the last 10 years'),
            ('20yo', 'Written in the last 20 years'),
        )

    def queryset(self, _, queryset):
        def book_filter(instances, year):
            return instances.filter(year__gte=year)
        if self.value() == '10yo':
            return book_filter(queryset, datetime.now().year - DECADE)
        elif self.value() == '20yo':
            return book_filter(queryset, datetime.now().year - DECADE * 2)
        return queryset


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    model = Book
    inlines = (BookAuthorInline, BookGenreInline)
    list_filter = (
        'genres',
        'type',
        RecencyBookFilter,
        'authors',
    )


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    model = Author
    inlines = (BookAuthorInline,)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    model = Genre


class BookClientInline(admin.TabularInline):
    model = BookClient
    extra = 1


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    model = Client
    inlines = (BookClientInline,)
