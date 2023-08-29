from rest_framework import serializers
from .models import Book, Serie
from .serializers_publisher import PublisherSimpleSerializer
from .serializers_genre import GenreForm
from .serializers_author import AuthorSimpleSerializer
from typing import Optional
from collections.abc import Iterable


class BookOverviewSerializer(serializers.ModelSerializer):
    language_code = serializers.SerializerMethodField()
    language = serializers.SerializerMethodField()
    cover = serializers.SerializerMethodField()
    genre = GenreForm()
    publisher = PublisherSimpleSerializer()
    authors = AuthorSimpleSerializer(many=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'original_title', 'language_code', 'language', 'cover', 'genre', 'publisher', 'publish_year', 'authors']

    def get_language_code(self, instance: Book) -> str:
        return instance.language

    def get_language(self, instance: Book) -> str:
        return instance.get_language_display()

    def get_cover(self, instance: Book) -> Optional[str]:
        if not instance.cover:
            return None
        return instance.cover.url


class BookForm(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['title', 'original_title', 'isbn', 'language', 'genre', 'back_text', 'publisher', 'publish_year']


# Defined here to prevent circular importing
class SerieBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Serie
        fields = ['id', 'name']
        read_only_fields = ['id', ]


class BookDetailSerializer(serializers.ModelSerializer):

    language_code = serializers.SerializerMethodField()
    language = serializers.SerializerMethodField()
    cover = serializers.SerializerMethodField()
    genre = GenreForm()
    publisher = PublisherSimpleSerializer()
    authors = AuthorSimpleSerializer(many=True)
    series = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'original_title', 'language_code', 'language', 'cover', 'genre', 'publisher', 'publish_year', 'authors', 'back_text', 'series']
        read_only_fields = fields

    def get_language_code(self, instance: Book) -> str:
        return instance.language

    def get_language(self, instance: Book) -> str:
        return instance.get_language_display()

    def get_cover(self, instance: Book) -> Optional[str]:
        if not instance.cover:
            return None
        return instance.cover.url

    def get_series(self, instance: Book) -> Iterable:
        return SerieBasicSerializer(instance.serie_set.all(), many=True).data
