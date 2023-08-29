from django.urls import path
import api.views as views

urlpatterns = [
    path('', views.get_random_selection),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('genre/', views.GenreOverview.as_view()),
    path('genre/all/', views.genre_tree),
    path('genre/<int:genre_id>/', views.GenreDetailView.as_view()),
    path('genre/<int:genre_id>/books/', views.get_books_for_subject, {'subject': 'genre'}),
    path('publisher/', views.PublisherOverview.as_view()),
    path('publisher/<int:publisher_id>/', views.PublisherDetailView.as_view()),
    path('publisher/<int:publisher_id>/books/', views.get_books_for_subject, {'subject': 'publisher'}),
    path('author/', views.AuthorOverview.as_view()),
    path('author/<int:author_id>/', views.AuthorDetailView.as_view()),
    path('author/<int:author_id>/books/', views.get_books_for_subject, {'subject': 'author'}),
    path('book/', views.BookOverview.as_view()),
    path('book/<int:book_id>/', views.BookDetailView.as_view()),
    path('book/<int:book_id>/cover/', views.BookCoverView.as_view()),
    path('serie/', views.SerieOverview.as_view()),
    path('serie/order/<int:order_id>/', views.SerieOrderingDetailView.as_view()),
    path('serie/<int:serie_id>/', views.SerieDetailView.as_view()),
    path('serie/<int:serie_id>/<book_id>/', views.SerieBookManagementView.as_view()),
]
