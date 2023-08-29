from rest_framework import serializers
from collections.abc import Mapping, Iterable
from .models import Genre, Book


class GenreOverviewSerializer(serializers.ModelSerializer):
    book_count = serializers.SerializerMethodField()

    class Meta:
        model = Genre
        fields = ['id', 'name', 'book_count']
        read_only_fields = ['id', 'book_count']

    def get_book_count(self, instance: Genre) -> int:

        list_of_genres = list()
        child_search = [instance.id, ]

        while len(child_search) > 0:
            next_to_search = child_search.pop()
            list_of_genres.append(next_to_search)

            for child in Genre.objects.filter(parent_id=next_to_search):
                child_search.append(child.id)

        book_count = Book.objects.filter(genre__in=list_of_genres).count()

        return book_count


class GenreForm(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name', 'parent']


class GenreDetailSerializer(serializers.ModelSerializer):
    parent = GenreForm(required=False, read_only=True)
    sub_genres = serializers.SerializerMethodField()
    book_count = serializers.SerializerMethodField()

    class Meta:
        model = Genre
        fields = ['id', 'name', 'parent', 'book_count', 'sub_genres']

    def get_sub_genres(self, instance: Genre) -> Iterable:
        subs = Genre.objects.filter(parent=instance)
        return GenreOverviewSerializer(subs, many=True).data

    def get_book_count(self, instance: Genre) -> int:
        return instance.book_count()

    @classmethod
    def get_root(cls) -> Mapping:
        return {
            'id': '0',
            'name': 'root',
            'parent': None,
            'book_count': Book.objects.all().count(),
            'sub_genres': GenreOverviewSerializer(Genre.objects.filter(parent__isnull=True), many=True).data,
        }