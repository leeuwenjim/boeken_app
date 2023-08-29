from django.urls import path
from . import views


urlpatterns = [
    path('', views.home),
    path('logout/', views.logout_view),
    path('login/', views.login_view),
    path('genres/', views.genres),
    path('books/', views.books, name='biblio-books'),
    path('books/<int:book_id>/', views.book_detail, name='biblio-books-details'),
    path('authors/', views.authors, name='biblio-authors'),
    path('authors/<int:author_id>/', views.author_details, name='biblio-authors-details'),
    path('series/', views.serie, name='biblio-serie'),
    path('series/<int:serie_id>/', views.serie_details, name='biblio-serie-details'),
    path('series/<int:serie_id>/ordering/', views.serie_order_overview, name='biblio-serie-ordering-details'),
    path('series/<int:serie_id>/ordering/new/', views.serie_order_edit, name='biblio-serie-ordering-new'),
    path('series/<int:serie_id>/ordering/<int:order_id>/', views.serie_order_edit, name='biblio-serie-ordering-edit'),
    path('publishers/', views.publishers, name='biblio-publisher'),
    path('publishers/<int:publisher_id>/', views.publisher_details, name='biblio-publisher-details'),
]
