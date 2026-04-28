"""
Database utility functions for the library management system.
These functions use raw SQL queries to efficiently retrieve data for the interface.

Usage examples:
    from books.utils import get_available_books, get_user_current_checkouts

    # Get all available books for the catalog
    available_books = get_available_books()

    # Get user's current checkouts for dashboard
    user_checkouts = get_user_current_checkouts(request.user.userID)

    # Search books by title
    search_results = search_books_by_title("Harry Potter")
"""

from django.db import connection
from django.utils import timezone
from .models import Book, Checkout, User, Author, Review, Reservation


def get_available_books():
    """
    Get all books that are currently available for checkout
    (not checked out and within circulation dates)
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT b.bookID, b.name, b.series_name, b.publisher, b.genre, b.price,
                   a.first as author_first, a.last as author_last
            FROM Books b
            JOIN Authors a ON b.authorID = a.authorID
            LEFT JOIN Checkouts c ON b.bookID = c.bookID AND c.in_time IS NULL
            WHERE c.bookID IS NULL
            AND (b.in_circulation_from IS NULL OR b.in_circulation_from <= CURRENT_DATE)
            AND (b.in_circulation_until IS NULL OR b.in_circulation_until >= CURRENT_DATE)
            ORDER BY b.name
        """)
        return cursor.fetchall()


def get_books_by_genre(genre):
    """Get all books in a specific genre"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT b.bookID, b.name, b.series_name, b.publisher, b.price,
                   a.first as author_first, a.last as author_last
            FROM Books b
            JOIN Authors a ON b.authorID = a.authorID
            WHERE b.genre = %s
            ORDER BY b.name
        """, [genre])
        return cursor.fetchall()


def get_overdue_books():
    """Get all currently overdue checkouts with user and book details"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.userID, c.bookID, c.out_time, c.due_time, c.fine,
                   u.first as user_first, u.last as user_last,
                   b.name as book_name, a.first as author_first, a.last as author_last
            FROM Checkouts c
            JOIN Users u ON c.userID = u.userID
            JOIN Books b ON c.bookID = b.bookID
            JOIN Authors a ON b.authorID = a.authorID
            WHERE c.in_time IS NULL AND c.due_time < CURRENT_TIMESTAMP
            ORDER BY c.due_time
        """)
        return cursor.fetchall()


def get_user_current_checkouts(user_id):
    """Get all books currently checked out by a user"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.bookID, c.out_time, c.due_time, c.fine,
                   b.name as book_name, b.series_name, b.genre,
                   a.first as author_first, a.last as author_last
            FROM Checkouts c
            JOIN Books b ON c.bookID = b.bookID
            JOIN Authors a ON b.authorID = a.authorID
            WHERE c.userID = %s AND c.in_time IS NULL
            ORDER BY c.due_time
        """, [user_id])
        return cursor.fetchall()


def get_user_checkout_history(user_id, limit=50):
    """Get user's checkout history (completed checkouts)"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.bookID, c.out_time, c.in_time, c.due_time, c.fine,
                   b.name as book_name, b.series_name,
                   a.first as author_first, a.last as author_last
            FROM Checkouts c
            JOIN Books b ON c.bookID = b.bookID
            JOIN Authors a ON b.authorID = a.authorID
            WHERE c.userID = %s AND c.in_time IS NOT NULL
            ORDER BY c.in_time DESC
            LIMIT %s
        """, [user_id, limit])
        return cursor.fetchall()


def get_popular_books(limit=10):
    """Get most popular books by checkout count"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT b.bookID, b.name, b.series_name, b.genre, COUNT(c.bookID) as checkout_count,
                   a.first as author_first, a.last as author_last
            FROM Books b
            JOIN Authors a ON b.authorID = a.authorID
            LEFT JOIN Checkouts c ON b.bookID = c.bookID
            GROUP BY b.bookID, b.name, b.series_name, b.genre, a.first, a.last
            ORDER BY checkout_count DESC
            LIMIT %s
        """, [limit])
        return cursor.fetchall()


def search_books_by_title(search_term):
    """Search books by title or series name"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT b.bookID, b.name, b.series_name, b.publisher, b.genre, b.price,
                   a.first as author_first, a.last as author_last
            FROM Books b
            JOIN Authors a ON b.authorID = a.authorID
            WHERE LOWER(b.name) LIKE LOWER(%s) OR LOWER(b.series_name) LIKE LOWER(%s)
            ORDER BY b.name
        """, [f'%{search_term}%', f'%{search_term}%'])
        return cursor.fetchall()


def get_books_by_author(author_id):
    """Get all books by a specific author"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT b.bookID, b.name, b.series_name, b.publisher, b.genre, b.price, b.pub_date
            FROM Books b
            WHERE b.authorID = %s
            ORDER BY b.pub_date DESC, b.name
        """, [author_id])
        return cursor.fetchall()


def get_user_balance(user_id):
    """Get user's current balance (sum of unpaid fines)"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COALESCE(SUM(c.fine), 0) as total_fines
            FROM Checkouts c
            WHERE c.userID = %s AND c.fine > 0
        """, [user_id])
        result = cursor.fetchone()
        return result[0] if result else 0


def get_book_reservation_queue(book_id):
    """Get all reservations for a book in order"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT r.userID, r.reservation_time,
                   u.first as user_first, u.last as user_last
            FROM Reservations r
            JOIN Users u ON r.userID = u.userID
            WHERE r.bookID = %s
            ORDER BY r.reservation_time
        """, [book_id])
        return cursor.fetchall()


def get_book_average_rating(book_id):
    """Get average rating for a book"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT AVG(r.score) as avg_rating, COUNT(r.score) as review_count
            FROM Reviews r
            WHERE r.bookID = %s
        """, [book_id])
        result = cursor.fetchone()
        return {
            'average_rating': result[0] if result[0] else 0,
            'review_count': result[1] if result[1] else 0
        }


def get_user_favorite_books(user_id):
    """Get user's favorite books"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT b.bookID, b.name, b.series_name, b.genre,
                   a.first as author_first, a.last as author_last
            FROM FavoriteBooks fb
            JOIN Books b ON fb.bookID = b.bookID
            JOIN Authors a ON b.authorID = a.authorID
            WHERE fb.userID = %s
            ORDER BY b.name
        """, [user_id])
        return cursor.fetchall()


def get_user_favorite_authors(user_id):
    """Get user's favorite authors"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.authorID, a.first, a.last, a.bio, a.city, a.country
            FROM FavoriteAuthors fa
            JOIN Authors a ON fa.authorID = a.authorID
            WHERE fa.userID = %s
            ORDER BY a.last, a.first
        """, [user_id])
        return cursor.fetchall()


def get_active_promotions():
    """Get all currently active promotions"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.promID, p.bookID, p.discount_percent, p.start_time, p.end_time,
                   b.name as book_name, b.price as original_price,
                   b.price * (1 - (p.discount_percent::numeric / 100)) as discounted_price,
                   a.first as author_first, a.last as author_last
            FROM Promotions p
            JOIN Books b ON p.bookID = b.bookID
            JOIN Authors a ON b.authorID = a.authorID
            WHERE p.start_time <= CURRENT_TIMESTAMP AND p.end_time >= CURRENT_TIMESTAMP
            ORDER BY p.end_time
        """)
        return cursor.fetchall()


def get_book_details_with_promotion(book_id):
    """Get book details including any active promotion"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT b.bookID, b.name, b.series_name, b.publisher, b.genre, b.price, b.pub_date,
                   a.authorID as author_id, a.first as author_first, a.last as author_last, a.bio as author_bio,
                   p.discount_percent, p.start_time, p.end_time
            FROM Books b
            JOIN Authors a ON b.authorID = a.authorID
            LEFT JOIN Promotions p ON b.bookID = p.bookID
                AND p.start_time <= CURRENT_TIMESTAMP AND p.end_time >= CURRENT_TIMESTAMP
            WHERE b.bookID = %s
        """, [book_id])
        result = cursor.fetchone()
        if result:
            return {
                'book_id': result[0],
                'name': result[1],
                'series_name': result[2],
                'publisher': result[3],
                'genre': result[4],
                'price': result[5],
                'pub_date': result[6],
                'author_id': result[7],
                'author_first': result[8],
                'author_last': result[9],
                'author_bio': result[10],
                'discount_percent': result[11],
                'promotion_start': result[12],
                'promotion_end': result[13],
                'discounted_price': result[5] * (1 - (result[11] / 100)) if result[11] else result[5]
            }
        return None