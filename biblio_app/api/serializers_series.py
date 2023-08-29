from rest_framework import serializers
from django.db.models.query import QuerySet
from .models import Serie, SeriesOrdering
from collections.abc import Iterable, Mapping
from .serializers_book import BookOverviewSerializer



class SeriesOverviewSerializer(serializers.ModelSerializer):
    book_count = serializers.SerializerMethodField()

    class Meta:
        model = Serie
        fields = ['id', 'name', 'book_count']
        read_only_fields = ['id', 'book_count']

    def get_book_count(self, instance: Serie) -> int:
        return instance.books.all().count()


class SeriesDetailSerializer(serializers.ModelSerializer):
    book_count = serializers.SerializerMethodField()
    books = serializers.SerializerMethodField()
    ordering = serializers.SerializerMethodField()

    class Meta:
        model = Serie
        fields = ['id', 'name', 'book_count', 'books', 'ordering']

    def __get_books(self, instance: Serie) -> QuerySet:
        if hasattr(self, 'book_query') and self.book_query is not None:
            return self.book_query
        self.book_query = instance.books.all().order_by('publish_year')
        return self.book_query


    def get_book_count(self, instance: Serie) -> int:
        books = self.__get_books(instance)
        return books.count()

    def get_books(self, instance: Serie) -> Iterable:
        return BookOverviewSerializer(self.__get_books(instance), many=True).data


    def get_ordering(self, instance: Serie) -> Mapping:
        books = self.__get_books(instance)
        result = {
            '0': {
                'name': 'Publicatie',
                'order': [str(book.id) for book in books]
            }
        }

        for ordering in instance.seriesordering_set.all():
            if ordering.book_order is None:
                book_order = None
            else:
                book_order = [int(book_id.strip()) for book_id in ordering.book_order.split(',')]

            result[ordering.id] = {
                'name': ordering.ordering_name,
                'order': book_order
            }
        return result


class SerieOrderingSerializer(serializers.ModelSerializer):
    serie = SeriesOverviewSerializer()
    ordering = serializers.SerializerMethodField()

    class Meta:
        model = SeriesOrdering
        fields = ['id', 'ordering_name', 'ordering', 'serie']

    def get_ordering(self, instance: SeriesOrdering) -> Iterable:
        if instance.book_order is None:
            return None
        return [int(book_id.strip()) for book_id in instance.book_order.split(',')]


class SerieOrderingForm(serializers.ModelSerializer):
    class Meta:
        model = SeriesOrdering
        fields = ['ordering_name', ]
