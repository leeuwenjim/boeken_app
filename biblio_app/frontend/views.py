from django.shortcuts import render, redirect
from django.views.decorators.http import require_safe, require_http_methods
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from api.models import Book, Publisher, Author, Serie, Genre, SeriesOrdering
from api.utils import generate_random_book_selection
from django.contrib.auth import login, authenticate, logout
from typing import Optional
from django.db.models import Case, When


@require_safe
def home(request: HttpRequest) -> HttpResponse:
    book_sample = generate_random_book_selection(5)
    return render(request, 'home.html', {'sample': book_sample})


@require_safe
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect('/')


@require_http_methods(['GET', 'POST'])
def login_view(request: HttpRequest) -> HttpResponse:
    context = {'username': ''}

    if request.method == 'POST':
        if 'username' not in request.POST or 'password' not in request.POST:
            return HttpResponse('INVALID USE OF THIS ENDPOINT', status=406)
        context['username'] = request.POST['username']

        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None or not user.is_active:
            context['error_message'] = 'Geen geldige gebruiker gevonden'
        else:
            login(request, user)
            return redirect('/')
    print(context)
    return render(request, 'login.html', context=context)


@require_safe
def genres(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect('/login/', permanent=False)
    context = {
        'genres': Genre.objects.all().order_by('name')
    }
    return render(request, 'genre_admin.html', context)


@require_safe
def books(request: HttpRequest) -> HttpResponse:
    return render(request, 'book_overview.html')


@require_safe
def book_detail(request: HttpRequest, book_id: int) -> HttpResponse:
    try:
        book: Book = Book.objects.prefetch_related('authors', 'publisher', 'serie_set', 'serie_set__books').get(id=book_id)
    except:
        return HttpResponse(status=404)
    return render(request, 'book_detail.html', {'book': book})


@require_safe
def serie(request: HttpRequest) -> HttpResponse:
    return render(request, 'serie_overview.html')


@require_safe
def serie_details(request: HttpRequest, serie_id: int) -> HttpResponse:
    try:
        serie = Serie.objects.get(id=serie_id)
    except Serie.DoesNotExist:
        return HttpResponse(status=404)

    ordering_methods = [{
            'id': 0,
            'name': 'Publicatie',
            'order': '0;' + ','.join([str(book.id) for book in serie.books.all().order_by('publish_year')])
        }
    ]

    for ordering in serie.seriesordering_set.all():
        if ordering.book_order is None:
            continue
        book_order = [book_id.strip() for book_id in ordering.book_order.split(',')]

        ordering_methods.append({
            'id': ordering.id,
            'name': ordering.ordering_name,
            'order': '{};{}'.format(ordering.id, ','.join(book_order))
        })

    context = {
        'serie': serie,
        'authors': Author.objects.filter(book__serie=serie).distinct(),
        'ordering': ordering_methods
    }

    print(context['ordering'])

    return render(request, 'serie_details.html', context)


@require_safe
def authors(request: HttpRequest) -> HttpResponse:
    return render(request, 'author_overview.html')

@require_safe
def author_details(request: HttpRequest, author_id: int) -> HttpResponse:
    try:
        author: Author = Author.objects.prefetch_related('book_set').get(id=author_id)
    except:
        return HttpResponse(status=404)

    return render(request, 'author_detail.html', {'author': author})


@require_safe
def publishers(request: HttpRequest) -> HttpResponse:
    return render(request, 'publisher_overview.html')

@require_safe
def publisher_details(request: HttpRequest, publisher_id: int) -> HttpResponse:
    try:
        publisher: Publisher = Publisher.objects.prefetch_related('book_set').get(id=publisher_id)
    except:
        return HttpResponse(status=404)
    return render(request, 'publisher_detail.html', {'publisher': publisher})


@require_safe
def serie_order_overview(request: HttpRequest, serie_id: int) -> HttpResponse:
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    try:
        serie: Serie = Serie.objects.get(id=serie_id)
    except Serie.DoesNotExist:
        return HttpResponse(status=404)

    context = {
        'serie': serie
    }

    return render(request, 'serie_ordering_overview.html', context=context)

@require_http_methods(['GET', 'POST'])
def serie_order_edit(request: HttpRequest, serie_id: int, order_id: Optional[int] = None) -> HttpResponse:
    if not request.user.is_authenticated:
        return HttpResponse(status=401)

    order = None

    try:
        serie: Serie = Serie.objects.get(id=serie_id)
    except Serie.DoesNotExist:
        return HttpResponse(status=404)

    if order_id is not None:
        try:
            order: SeriesOrdering = SeriesOrdering.objects.get(id=order_id)
        except SeriesOrdering.DoesNotExist:
            return HttpResponse(status=404)

        pk_list = [int(book_id) for book_id in order.book_order.split(',')]
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
        books = Book.objects.filter(pk__in=pk_list).order_by(preserved)
    else:
        books = serie.books.all().order_by('publish_year')

    context = {
        'serie': serie,
        'order': order,
        'books':books
    }
    return render(request, 'serie_ordering_form.html', context=context)
