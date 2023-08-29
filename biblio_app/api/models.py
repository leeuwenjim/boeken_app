from django.db import models
import re


def cover_upload_location(instance, filename):
    title_dir = re.sub(r'[^\w\s]', '', instance.title)
    title_dir = re.sub(r'\s+', '_', title_dir)
    return 'covers/{}/{}'.format(title_dir, filename)


class Genre(models.Model):
    name = models.CharField(null=False, blank=False, max_length=100, unique=True)
    parent = models.ForeignKey('Genre', on_delete=models.SET_NULL, null=True, blank=True)

    def book_count(self):
        list_of_genres = list()
        child_search = [self.id, ]

        while len(child_search) > 0:
            next_to_search = child_search.pop()
            list_of_genres.append(next_to_search)

            for child in Genre.objects.filter(parent_id=next_to_search):
                child_search.append(child.id)

        return Book.objects.filter(genre__in=list_of_genres).count()

    def __str__(self):
        return f'<Genre: {self.name}>'


    def __repr__(self):
        return self.__str__()


class Author(models.Model):
    first_name = models.CharField(null=False, blank=False, max_length=100)
    last_name = models.CharField(null=False, blank=False, max_length=150)
    alias_for = models.ForeignKey('Author', null=True, blank=True, on_delete=models.SET_NULL)

    def get_full_name(self):
        return '{0} {1}'.format(self.first_name, self.last_name).strip()

    @property
    def book_count_total(self):
        author_ids = [self.id, ]
        for alias in Author.objects.filter(alias_for=self):
            author_ids.append(alias.id)
        return Book.objects.filter(authors__in=author_ids).count()

    @property
    def aliases_set(self):
        return Author.objects.filter(alias_for=self)

    def __str__(self):
        return f'<Author: {self.first_name} {self.last_name}>'


    def __repr__(self):
        return self.__str__()


class Publisher(models.Model):
    name = models.CharField(null=False, blank=False, max_length=200)

    def __str__(self):
        return f'<Publisher: {self.name}>'


    def __repr__(self):
        return self.__str__()


class Book(models.Model):
    class LanguageChoices(models.TextChoices):
        DUTCH = 'NL', 'Nederlands'
        ENGLISH = 'GB', 'Engels'
        SWEDISH = 'SE', 'Zweeds'
        GERMAN = 'DE', 'Duits'
        FRENCH = 'FR', 'Frans'
        SPANISH = 'ES', 'Spaans'

    title = models.CharField(null=False, blank=False, max_length=200)
    original_title = models.CharField(null=True, blank=True, max_length=200)
    isbn = models.CharField(null=True, blank=True, max_length=15)
    language = models.CharField(max_length=3, null=False, blank=False, choices=LanguageChoices.choices, default=LanguageChoices.DUTCH)
    cover = models.ImageField(upload_to=cover_upload_location, max_length=250, null=True, blank=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    back_text = models.TextField(null=True, blank=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True)
    publish_year = models.IntegerField(null=True, blank=True)
    authors = models.ManyToManyField(Author)

    def formatted_isbn(self):
        if self.isbn is None:
            return None
        if len(self.isbn) == 13:
            return f'{self.isbn[0:3]}-{self.isbn[3:5]}-{self.isbn[5:8]}-{self.isbn[8:12]}-{self.isbn[12]}'
        return self.isbn

    def __str__(self):
        return f'<Book: {self.title}>'


    def __repr__(self):
        return self.__str__()


class Serie(models.Model):
    class Meta:
        ordering = ['name', ]

    name = models.CharField(null=False, blank=False, max_length=200)
    books = models.ManyToManyField(Book)

    def __str__(self):
        return f'<Serie: {self.name}>'


    def __repr__(self):
        return self.__str__()

    def add_book(self, book: Book):
        self.books.add(book)
        for ordering in self.seriesordering_set.all():
            ordering.book_order = ordering.book_order + f',{book.id}'
            ordering.save()

    def remove_book(self, book: Book):
        self.books.remove(book)
        for ordering in self.seriesordering_set.all():
            id_list = [book_id for book_id in ordering.book_order.split(',') if int(book_id) != book.id]
            ordering.book_order = ','.join(id_list)
            ordering.save()

    def get_books(self):
        return self.books.all().order_by('publish_year')


class SeriesOrdering(models.Model):
    ordering_name = models.CharField(null=False, blank=False, max_length=100)
    serie = models.ForeignKey(Serie, on_delete=models.CASCADE)
    book_order = models.TextField(max_length=250, null=True, blank=True)

    def __str__(self):
        return f'<SeriesOrdering: {self.ordering_name} for {self.serie.name}>'


    def __repr__(self):
        return self.__str__()

