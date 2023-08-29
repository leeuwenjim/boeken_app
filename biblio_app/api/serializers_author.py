from rest_framework import serializers
from .models import Author
from collections.abc import Iterable


class AuthorForm(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'alias_for']


class AuthorSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name']
        read_only_fields = ['id', ]

class AuthorSerializer(serializers.ModelSerializer):
    book_count = serializers.SerializerMethodField()
    alias_for = AuthorSimpleSerializer()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name', 'full_name', 'alias_for', 'book_count']
        read_only_fields = ['id', 'book_count']

    def get_full_name(self, instance: Author) -> str:
        return instance.get_full_name()

    def get_book_count(self, instance: Author) -> int:
        return instance.book_set.count()


class AuthorDetailSerializer(serializers.ModelSerializer):
    book_count = serializers.SerializerMethodField()
    aliases = serializers.SerializerMethodField()
    alias_for = AuthorSimpleSerializer()

    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name', 'alias_for', 'aliases', 'book_count']
        read_only_fields = ['id', 'book_count']

    def get_book_count(self, instance: Author) -> int:
        return instance.book_set.count()

    def get_aliases(self, instance: Author) -> Iterable:
        return AuthorSerializer(Author.objects.filter(alias_for=instance), many=True).data
