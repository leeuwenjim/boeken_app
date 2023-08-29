from rest_framework import serializers
from .models import Publisher, Book


class PublisherSerializer(serializers.ModelSerializer):
    book_count = serializers.SerializerMethodField()

    class Meta:
        model = Publisher
        fields = ['id', 'name', 'book_count']
        read_only_fields = ['id', 'book_count']

    def get_book_count(self, instance: Publisher) -> int:
        return Book.objects.filter(publisher=instance).count()


class PublisherSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['id', 'name']
        read_only_fields = ['id']
