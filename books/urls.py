from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    # Book catalog and search
    path('', views.book_catalog, name='catalog'),
    path('search/', views.book_catalog, name='search'),  # Reuses catalog view with search param

    # Book details and actions
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('book/<int:book_id>/checkout/', views.checkout_book, name='checkout_book'),
    path('book/<int:book_id>/return/', views.return_book, name='return_book'),
    path('book/<int:book_id>/reserve/', views.reserve_book, name='reserve_book'),
    path('book/<int:book_id>/favorite/', views.add_favorite_book, name='add_favorite_book'),

    # Author pages
    path('author/<int:author_id>/', views.author_detail, name='author_detail'),
    path('author/<int:author_id>/favorite/', views.add_favorite_author, name='add_favorite_author'),

    # User dashboard
    path('dashboard/', views.user_dashboard, name='user_dashboard'),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Popular books and promotions
    path('popular/', views.popular_books, name='popular_books'),
    path('promotions/', views.promotions, name='promotions'),
]