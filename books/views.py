from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .utils import (
    get_available_books, get_books_by_genre, get_user_current_checkouts,
    get_user_checkout_history, get_popular_books, search_books_by_title,
    get_books_by_author, get_user_balance, get_book_reservation_queue,
    get_book_average_rating, get_user_favorite_books, get_user_favorite_authors,
    get_active_promotions, get_book_details_with_promotion
)
from .models import Book, Author, User, Checkout, Reservation, Review


def login_view(request):
    """
    Simple login by entering a user ID from the preloaded users table.
    """
    if request.method == 'POST':
        user_id_str = request.POST.get('user_id')
        if user_id_str:
            try:
                user_id = int(user_id_str)
                user = authenticate(request, user_id=user_id)
                if user:
                    login(request, user)
                    messages.success(request, f"Logged in as {user.first} {user.last}.")
                    return redirect('books:user_dashboard')
                else:
                    messages.error(request, 'User ID not found. Please check your User ID and try again.')
            except ValueError:
                messages.error(request, 'User ID must be a valid number.')
        else:
            messages.error(request, 'Please enter a User ID.')

    return render(request, 'books/login.html')


@login_required
def logout_view(request):
    """Logout the currently logged-in user."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('books:catalog')


def book_catalog(request):
    """
    Display all available books in the catalog
    """
    # Get filter parameters
    genre = request.GET.get('genre')
    search = request.GET.get('search')

    if search:
        books = search_books_by_title(search)
        context = {'books': books, 'search_term': search, 'is_search': True}
    elif genre:
        books = get_books_by_genre(genre)
        context = {'books': books, 'selected_genre': genre, 'is_filtered': True}
    else:
        books = get_available_books()
        context = {'books': books}

    # Get unique genres for filter dropdown
    genres = Book.objects.values_list('genre', flat=True).distinct().exclude(genre__isnull=True)
    context['genres'] = sorted(genres)

    return render(request, 'books/catalog.html', context)


def book_detail(request, book_id):
    """
    Display detailed information about a specific book
    """
    book_data = get_book_details_with_promotion(book_id)
    if not book_data:
        # Book not found
        return render(request, 'books/book_not_found.html', {'book_id': book_id})

    # Get additional book information
    rating_data = get_book_average_rating(book_id)
    reservation_queue = get_book_reservation_queue(book_id)

    # Get reviews for this book
    reviews = Review.objects.filter(book_id=book_id).select_related('user').order_by('-id')[:10]

    context = {
        'book': book_data,
        'rating': rating_data,
        'reviews': reviews,
        'reservation_count': len(reservation_queue),
        'is_available': len(reservation_queue) == 0,  # Simple availability check
    }

    return render(request, 'books/book_detail.html', context)


@login_required
def user_dashboard(request):
    """
    Display user's dashboard with current checkouts, history, and favorites
    """
    user_id = request.user.userID

    current_checkouts = get_user_current_checkouts(user_id)
    checkout_history = get_user_checkout_history(user_id, limit=10)
    user_balance = get_user_balance(user_id)
    favorite_books = get_user_favorite_books(user_id)
    favorite_authors = get_user_favorite_authors(user_id)
    now = timezone.now()

    context = {
        'current_checkouts': current_checkouts,
        'checkout_history': checkout_history,
        'user_balance': user_balance,
        'favorite_books': favorite_books,
        'favorite_authors': favorite_authors,
        'overdue_count': sum(1 for checkout in current_checkouts if checkout[2] < now),  # due_time index
        'now': now,
    }

    return render(request, 'books/dashboard.html', context)


def author_detail(request, author_id):
    """
    Display author information and their books
    """
    try:
        author = Author.objects.get(authorID=author_id)
    except Author.DoesNotExist:
        return render(request, 'books/author_not_found.html', {'author_id': author_id})

    books = get_books_by_author(author_id)

    context = {
        'author': author,
        'books': books,
        'book_count': len(books),
    }

    return render(request, 'books/author_detail.html', context)


def popular_books(request):
    """
    Display most popular books by checkout count
    """
    books = get_popular_books(limit=20)
    return render(request, 'books/popular.html', {'books': books})


@login_required
def checkout_book(request, book_id):
    """
    Handle book checkout process
    """
    if request.method != 'POST':
        return redirect('books:book_detail', book_id=book_id)

    user_id = request.user.userID

    # Check if book is available
    available_books = get_available_books()
    book_available = any(book[0] == book_id for book in available_books)  # bookID is first column

    if not book_available:
        messages.error(request, "This book is not currently available for checkout.")
        return redirect('books:book_detail', book_id=book_id)

    # Check if user already has this book checked out
    existing_checkout = Checkout.objects.filter(
        user_id=user_id,
        book_id=book_id,
        in_time__isnull=True
    ).exists()

    if existing_checkout:
        messages.error(request, "You already have this book checked out.")
        return redirect('books:book_detail', book_id=book_id)

    try:
        with transaction.atomic():
            # Create checkout record
            due_date = timezone.now() + timezone.timedelta(days=14)  # 2 weeks default
            checkout = Checkout.objects.create(
                user_id=user_id,
                book_id=book_id,
                out_time=timezone.now(),
                due_time=due_date,
                fine=0.00
            )

            messages.success(request, f"Successfully checked out book. Due date: {due_date.date()}")
            return redirect('books:user_dashboard')

    except Exception as e:
        messages.error(request, "An error occurred while checking out the book. Please try again.")
        return redirect('books:book_detail', book_id=book_id)


@login_required
def return_book(request, book_id):
    """
    Handle book return process
    """
    if request.method != 'POST':
        return redirect('books:user_dashboard')

    user_id = request.user.userID

    try:
        with transaction.atomic():
            # Find the active checkout for this user and book
            checkout = Checkout.objects.get(
                user_id=user_id,
                book_id=book_id,
                in_time__isnull=True
            )

            # Update return time
            checkout.in_time = timezone.now()

            # Calculate any fines (simplified - $0.50 per day overdue)
            if checkout.due_time < checkout.in_time:
                days_overdue = (checkout.in_time - checkout.due_time).days
                checkout.fine = max(0, days_overdue * 0.50)

            checkout.save()

            if checkout.fine > 0:
                messages.warning(request, f"Book returned successfully. Late fee: ${checkout.fine:.2f}")
            else:
                messages.success(request, "Book returned successfully!")

            return redirect('books:user_dashboard')

    except Checkout.DoesNotExist:
        messages.error(request, "No active checkout found for this book.")
        return redirect('books:user_dashboard')
    except Exception as e:
        messages.error(request, "An error occurred while returning the book. Please try again.")
        return redirect('books:user_dashboard')


@login_required
def reserve_book(request, book_id):
    """
    Handle book reservation process
    """
    if request.method != 'POST':
        return redirect('books:book_detail', book_id=book_id)

    user_id = request.user.userID

    # Check if user already has this book checked out
    existing_checkout = Checkout.objects.filter(
        user_id=user_id,
        book_id=book_id,
        in_time__isnull=True
    ).exists()

    if existing_checkout:
        messages.warning(request, "You already have this book checked out.")
        return redirect('books:book_detail', book_id=book_id)

    # Check if user already has a reservation for this book
    existing_reservation = Reservation.objects.filter(user_id=user_id, book_id=book_id).exists()

    if existing_reservation:
        messages.warning(request, "You already have a reservation for this book.")
        return redirect('books:book_detail', book_id=book_id)

    try:
        with transaction.atomic():
            Reservation.objects.create(
                user_id=user_id,
                book_id=book_id,
                reservation_time=timezone.now()
            )

            messages.success(request, "Book reserved successfully! You'll be notified when it becomes available.")
            return redirect('books:book_detail', book_id=book_id)

    except Exception as e:
        messages.error(request, "An error occurred while reserving the book. Please try again.")
        return redirect('books:book_detail', book_id=book_id)


@login_required
def add_favorite_book(request, book_id):
    """
    Add a book to user's favorites
    """
    if request.method != 'POST':
        return redirect('books:book_detail', book_id=book_id)

    user_id = request.user.userID

    try:
        from .models import FavoriteBook
        FavoriteBook.objects.get_or_create(
            user_id=user_id,
            book_id=book_id,
            author_id=Book.objects.get(bookID=book_id).author_id
        )
        messages.success(request, "Book added to favorites!")
    except Exception as e:
        messages.error(request, "Could not add book to favorites.")

    return redirect('books:book_detail', book_id=book_id)


@login_required
def add_favorite_author(request, author_id):
    """
    Add an author to user's favorites
    """
    if request.method != 'POST':
        return redirect('books:author_detail', author_id=author_id)

    user_id = request.user.userID

    try:
        from .models import FavoriteAuthor
        FavoriteAuthor.objects.get_or_create(
            user_id=user_id,
            author_id=author_id
        )
        messages.success(request, "Author added to favorites!")
    except Exception as e:
        messages.error(request, "Could not add author to favorites.")

    return redirect('books:author_detail', author_id=author_id)


def promotions(request):
    """
    Display current active promotions
    """
    promotions = get_active_promotions()
    return render(request, 'books/promotions.html', {'promotions': promotions})
