from rest_framework.serializers import HyperlinkedModelSerializer
from .models import Book, Author, Genre


class BookSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Book
        fields = ('id', 'title', 'description', 'type', 'year', 'age_limit', 'volume', 'created', 'modified')


class AuthorSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Author
        fields = ('id', 'full_name')


class GenreSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Genre
        fields = ('id', 'name', 'description')
