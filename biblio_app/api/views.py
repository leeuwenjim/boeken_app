from django.db.models import Q, Value, Count
from django.db.models.functions import Concat
from rest_framework import views
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import (
    Genre,
    Book,
    Publisher,
    Author,
    Serie,
    SeriesOrdering,
)
from .serializers_genre import (
    GenreOverviewSerializer,
    GenreForm,
    GenreDetailSerializer,
)
from .serializers_book import (
    BookOverviewSerializer,
    BookForm,
    BookDetailSerializer,
)
from .serializers_author import (
    AuthorSerializer,
    AuthorDetailSerializer,
    AuthorForm,
)
from .serializers_series import (
    SeriesOverviewSerializer,
    SeriesDetailSerializer,
    SerieOrderingSerializer,
    SerieOrderingForm,
)
from .serializers_publisher import PublisherSerializer
from rest_framework.request import Request
from biblio_app.views import DetailApiView, allow_zero, protect
import random
from biblio_app.pagination import ApiRestPagination
from django.contrib.auth import login, authenticate, logout
from .validation import validate_book_order_field
from .utils import get_ordering, generate_filters, generate_random_book_selection


@api_view(['POST', ])
def login_view(request: Request) -> Response:
    if request.user.is_authenticated:
        return Response(status=status.HTTP_200_OK)
    if not('username' in request.data and 'password' in request.data):
        return Response({'error': 'username and password are required'}, status.HTTP_400_BAD_REQUEST)
    username = request.data['username']
    password = request.data['password']

    user = authenticate(request, username=username, password=password)
    if user is None or not user.is_active:
        return Response({'error': 'Incorrect credentials'}, status=status.HTTP_400_BAD_REQUEST)
    login(request, user)
    return Response(status=status.HTTP_200_OK)

@api_view(['GET', ])
def logout_view(request: Request) -> Response:
    logout(request)
    return Response(status=status.HTTP_200_OK)


@api_view(['GET', ])
def genre_tree(request: Request) -> Response:
    all_genres = Genre.objects.all().order_by('name')
    genre_tree = []
    object_map = dict()

    object_map['0'] = {
        'id': 0,
        'name': 'Alles',
        'book_count': Book.objects.all().count(),
        'parent': None,
        'children': list()
    }

    for item in all_genres:
        item_key = str(item.id)
        if item_key in object_map: continue
        object_map[item_key] = {
            'id': item.id,
            'name': item.name,
            'book_count': item.book_count(),
            'parent': item.parent if item.parent is None else item.parent.id,
            'children': list()
        }

    for key in object_map:
        item = object_map[key]
        if item['parent'] is None:
            genre_tree.append(item)
        else:
            parent_key = str(item['parent'])
            object_map[parent_key]['children'].append(item)

    return Response(genre_tree)



@api_view(['GET', ])
def get_random_selection(request: Request) -> Response:
    amount = 5
    max_amount = 10

    if 'n' in request.query_params:
        try:
            amount = int(request.query_params['n'])
        except ValueError:
            pass

    samples = get_random_selection(amount, max_amount)

    return Response(BookOverviewSerializer(samples, many=True).data)



@api_view(['GET', ])
def get_books_for_subject(request: Request, subject: str, **kwargs) -> Response:
    response_404 = Response(status=status.HTTP_404_NOT_FOUND)

    ordering = get_ordering(request, 'order', ['title', 'original_title', 'isbn', 'publish_year'])

    title_filter = generate_filters(Book, request.query_params, ['title','original_title'], use_or=True)
    search_filter = generate_filters(Book, request.query_params, ['isbn', 'authors', 'genre', 'publisher', 'publish_year'])

    try:
        if subject == 'genre':
            if 'genre_id' not in kwargs:
                return response_404

            start_genre_id = int(kwargs['genre_id'])

            if start_genre_id == 0:
                books = Book.objects.filter(search_filter).filter(title_filter).order_by(ordering)
            else:
                list_of_genres = list()
                child_search = [start_genre_id, ]

                while len(child_search) > 0:
                    next_to_search = child_search.pop()
                    list_of_genres.append(next_to_search)

                    for child in Genre.objects.filter(parent_id=next_to_search):
                        child_search.append(child.id)

                books = Book.objects.filter(genre__in=list_of_genres).filter(search_filter).filter(title_filter).order_by(ordering)
        elif subject == 'publisher':
            if 'publisher_id' not in kwargs:
                return response_404
            books = Book.objects.filter(publisher_id=int(kwargs['publisher_id'])).filter(search_filter).filter(title_filter).order_by(ordering)
        elif subject == 'author':
            if 'author_id' not in kwargs:
                return response_404
            try:
                author = Author.objects.get(id=int(kwargs['author_id']))
            except ValueError:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            except Author.DoesNotExist:
                return response_404

            books = author.book_set.filter(search_filter).filter(title_filter).order_by(ordering)
        else:
            return response_404
    except ValueError:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    return ApiRestPagination().paginate(query_set=books, request=request, serializer=BookOverviewSerializer)


class GenreOverview(views.APIView):
    @staticmethod
    def get(request: Request) -> Response:

        search = generate_filters(Genre, request.query_params, ['name', 'parent'])

        ordering = get_ordering(request, 'order', ['name', ])

        genres = Genre.objects.filter(search).order_by(ordering)

        return ApiRestPagination().paginate(query_set=genres, request=request, serializer=GenreOverviewSerializer)

    @staticmethod
    @protect
    def post(request: Request) -> Response:
        serializer = GenreForm(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(GenreOverviewSerializer(serializer.instance).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenreDetailView(DetailApiView):

    model = Genre
    id_name = 'genre_id'
    keyword = 'genre'

    @staticmethod
    @allow_zero
    def get(request: Request, genre: Genre) -> Response:
        if genre is None:
            return Response(GenreDetailSerializer.get_root())
        return Response(GenreDetailSerializer(genre).data)

    @staticmethod
    @protect
    def put(request: Request, genre: Genre) -> Response:
        validator = GenreForm(instance=genre, data=request.data, partial=True)
        if validator.is_valid():
            validator.save()
            return Response(GenreDetailSerializer(instance=validator.instance).data, status=status.HTTP_202_ACCEPTED)
        return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    @protect
    def delete(request: Request, genre: Genre) -> Response:
        if genre.parent is not None:
            Genre.objects.filter(parent=genre).update(parent=genre.parent)
        genre.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PublisherOverview(views.APIView):
    @staticmethod
    def get(request: Request) -> Response:

        search = generate_filters(Publisher, request.query_params, ['name', ])

        ordering = get_ordering(request, 'order', ['name', 'book_count'])

        publishers = Publisher.objects.annotate(book_count=Count("book")).filter(search).order_by(ordering)

        return ApiRestPagination().paginate(query_set=publishers, request=request, serializer=PublisherSerializer)


    @staticmethod
    @protect
    def post(request: Request) -> Response:
        serializer = PublisherSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PublisherDetailView(DetailApiView):
    model = Publisher
    id_name = 'publisher_id'
    keyword = 'publisher'

    @staticmethod
    def get(request: Request, publisher: Publisher) -> Response:
        return Response(PublisherSerializer(publisher).data)

    @staticmethod
    @protect
    def put(request: Request, publisher: Publisher) -> Response:
        serializer = PublisherSerializer(publisher, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    @protect
    def delete(request: Request, publisher: Publisher) -> Response:
        publisher.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AuthorOverview(views.APIView):
    @staticmethod
    def get(request: Request) -> Response:
        search_filters = generate_filters(Author, request.query_params, ['first_name', 'last_name'], ['full_name', ])

        ordering = get_ordering(request, 'order', ['full_name', 'book_count', 'first_name', 'last_name'])
        authors = Author.objects.annotate(book_count=Count("book")).annotate(full_name=Concat('first_name', Value(' '), 'last_name')).filter(search_filters).order_by(ordering)

        return ApiRestPagination().paginate(query_set=authors, request=request, serializer=AuthorSerializer)


    @staticmethod
    @protect
    def post(request: Request) -> Response:
        serializer = AuthorForm(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(AuthorSerializer(serializer.instance).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthorDetailView(DetailApiView):
    model = Author
    id_name = 'author_id'
    keyword = 'author'

    @staticmethod
    def get(request: Request, author: Author) -> Response:
        return Response(AuthorDetailSerializer(author).data)

    @staticmethod
    @protect
    def put(request: Request, author: Author) -> Response:
        serializer = AuthorForm(author, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(AuthorSerializer(serializer.instance).data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    @protect
    def delete(request: Request, author: Author) -> Response:
        author.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookOverview(views.APIView):
    @staticmethod
    def get(request: Request) -> Response:
        search_filters = generate_filters(Book, request.query_params, ['isbn', 'authors', 'genre', 'publisher', 'publish_year'])
        title_filter = generate_filters(Book, request.query_params, ['title','original_title'], use_or=True)

        ordering = get_ordering(request, 'order', ['title', 'original_title', 'isbn', 'publish_year'])

        books = Book.objects.filter(search_filters).filter(title_filter).order_by(ordering)

        return ApiRestPagination().paginate(query_set=books, request=request, serializer=BookOverviewSerializer)

    @staticmethod
    @protect
    def post(request: Request) -> Response:
        serializer = BookForm(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        authors = []
        if 'authors' in request.data:
            print('authors data found')
            if request.data['authors'] != '':
                print(f'data not empty: {request.data["authors"]}')
                try:
                    author_ids = [int(author_id.strip()) for author_id in request.data['authors'].split(',')]
                    authors = Author.objects.filter(id__in=author_ids)
                    print(f'found authors: {authors}')
                except ValueError:
                    return Response({'authors': [f'Invalid ID found in the comma seperated author id list: {request.data["authors"]}', ]}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        book: Book = serializer.instance
        book.authors.add(*list(authors))

        return Response(BookDetailSerializer(book).data, status=status.HTTP_201_CREATED)


class BookDetailView(DetailApiView):
    model = Book
    id_name = 'book_id'
    keyword = 'book'

    @staticmethod
    def get(request: Request, book: Book):
        return Response(BookDetailSerializer(book).data)

    @staticmethod
    @protect
    def put(request: Request, book: Book):

        serializer = BookForm(book, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        current_id_set = {str(author.id) for author in book.authors.all()}
        authors_to_add = []
        authors_to_remove = []

        if 'authors' in request.data:
            if request.data['authors'] == '':
                authors_to_remove = book.authors.all()
            else:
                try:
                    given_ids = [given_id.strip() for given_id in request.data['authors'].split(',')]

                    author_to_add_ids = [int(author_id) for author_id in given_ids if author_id not in current_id_set]
                    authors_to_add = Author.objects.filter(id__in=author_to_add_ids)

                    authors_to_remove_ids = [int(author_id) for author_id in current_id_set if author_id not in given_ids]
                    authors_to_remove = Author.objects.filter(id__in=authors_to_remove_ids)

                except ValueError:
                    return Response(
                        {'authors': [f'Invalid ID found in the comma seperated author id list: {request.data["authors"]}', ]}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        book: Book = serializer.instance
        book.authors.add(*list(authors_to_add))
        book.authors.remove(*list(authors_to_remove))

        return Response(BookDetailSerializer(book).data, status=status.HTTP_202_ACCEPTED)

    @staticmethod
    @protect
    def delete(request: Request, book: Book):
        book.cover.delete()
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SerieOverview(views.APIView):
    @staticmethod
    def get(request: Request) -> Response:
        search_filters = generate_filters(Serie, request.query_params, ['name', ])

        ordering = get_ordering(request, 'order', ['name', 'book_count'])

        series = Serie.objects.annotate(book_count=Count("books")).filter(search_filters).order_by(ordering)

        return ApiRestPagination().paginate(query_set=series, request=request, serializer=SeriesOverviewSerializer)

    @staticmethod
    @protect
    def post(request: Request) -> Response:
        serializer = SeriesOverviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SerieDetailView(DetailApiView):
    model = Serie
    id_name = 'serie_id'
    keyword = 'serie'

    @staticmethod
    def get(request: Request, serie: Serie) -> Response:
        return Response(SeriesDetailSerializer(serie).data)

    @staticmethod
    @protect
    def post(request: Request, serie: Serie) -> Response:
        serializer = SerieOrderingForm(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        errors = validate_book_order_field(request.data, serie)

        if len(errors):
            return Response({'book_order': errors}, status=status.HTTP_400_BAD_REQUEST)


        serie_order: SeriesOrdering = serializer.save(serie=serie)
        serie_order.book_order = ','.join([str(book_id) for book_id in request.data['book_order']])
        serie_order.save()

        return Response(SerieOrderingSerializer(serie_order).data, status=status.HTTP_201_CREATED)

    @staticmethod
    @protect
    def put(request: Request, serie: Serie) -> Response:
        serializer = SeriesOverviewSerializer(serie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    @protect
    def delete(request: Request, serie: Serie) -> Response:
        serie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SerieOrderingDetailView(DetailApiView):
    model = SeriesOrdering
    id_name = 'order_id'
    keyword = 'order'

    @staticmethod
    def get(request: Request, order: SeriesOrdering) -> Response:
        return Response(SerieOrderingSerializer(order).data)

    @staticmethod
    @protect
    def put(request: Request, order: SeriesOrdering) -> Response:

        serializer = SerieOrderingForm(order, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        errors = validate_book_order_field(request.data, order.serie)

        if len(errors):
            return Response({'book_order': errors}, status=status.HTTP_400_BAD_REQUEST)

        serie_order: SeriesOrdering = serializer.save()
        serie_order.book_order = ','.join([str(book_id) for book_id in request.data['book_order']])
        serie_order.save()

        return Response(SerieOrderingSerializer(serie_order).data, status=status.HTTP_202_ACCEPTED)

    @staticmethod
    @protect
    def delete(request: Request, order: SeriesOrdering) -> Response:
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookCoverView(DetailApiView):
    model = Book
    id_name = 'book_id'
    keyword = 'book'

    @staticmethod
    def get(request: Request, book: Book) -> Response:
        if book.cover:
            return Response({'cover': book.cover.url})
        return Response({'cover': None})

    @staticmethod
    @protect
    def put(request: Request, book: Book) -> Response:

        if book.cover:
            book.cover.delete()

        book.cover = request.data['cover']
        book.save()
        return Response({'cover': book.cover.url}, status=status.HTTP_202_ACCEPTED)

    @staticmethod
    @protect
    def delete(request: Request, book: Book) -> Response:
        if book.cover:
            book.cover.delete()
        return Response({'cover': None}, status=status.HTTP_202_ACCEPTED)


class SerieBookManagementView(views.APIView):
    @staticmethod
    @protect
    def post(request: Request, serie_id: int, book_id: int) -> Response:
        try:
            serie = Serie.objects.get(id=serie_id)
            book = Book.objects.get(id=book_id)
        except (Serie.DoesNotExist, Book.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)

        serie.add_book(book)

        return Response(status=status.HTTP_202_ACCEPTED)

    @staticmethod
    @protect
    def delete(request: Request, serie_id: int, book_id: int) -> Response:
        try:
            serie = Serie.objects.get(id=serie_id)
            book = Book.objects.get(id=book_id)
        except (Serie.DoesNotExist, Book.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)

        serie.remove_book(book)

        return Response(status=status.HTTP_202_ACCEPTED)
