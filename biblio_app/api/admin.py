from django.contrib import admin
from .models import Publisher, Author, Book, Serie, SeriesOrdering, Genre

# Register your models here.
admin.site.register(Publisher)
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Book)
admin.site.register(Serie)
admin.site.register(SeriesOrdering)