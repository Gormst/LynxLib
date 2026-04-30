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


def get_catalog_genres():
    """Get genres available for catalog filtering."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT genre
            FROM Books
            WHERE genre IS NOT NULL AND genre <> ''
            ORDER BY genre
        """)
        return [row[0] for row in cursor.fetchall()]


def get_author_by_id(author_id):
    """Get author details by ID."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT authorID, first, last, bio, city, country
            FROM Authors
            WHERE authorID = %s
        """, [author_id])
        row = cursor.fetchone()

    if not row:
        return None

    return {
        'authorID': row[0],
        'first': row[1],
        'last': row[2],
        'bio': row[3],
        'city': row[4],
        'country': row[5],
    }


def get_available_books():
    """
    Get all books that are currently available for checkout
    (not checked out and within circulation dates)
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT b.bookID, b.name, b.series_name, b.publisher, b.genre, b.price,
                   a.first as author_first, a.last as author_last, a.authorID
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
            SELECT b.bookID, b.name, b.series_name, b.publisher, b.genre, b.price,
                   a.first as author_first, a.last as author_last, a.authorID
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
                   a.first as author_first, a.last as author_last, a.authorID
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
                   a.first as author_first, a.last as author_last, a.authorID
            FROM Checkouts c
            JOIN Books b ON c.bookID = b.bookID
            JOIN Authors a ON b.authorID = a.authorID
            WHERE c.userID = %s AND c.in_time IS NOT NULL
            ORDER BY c.in_time DESC
            LIMIT %s
        """, [user_id, limit])
        return cursor.fetchall()


def user_has_active_checkout(user_id, book_id):
    """Check whether a user already has a book checked out."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 1
            FROM Checkouts
            WHERE userID = %s
              AND bookID = %s
              AND in_time IS NULL
        """, [user_id, book_id])
        return cursor.fetchone() is not None


def checkout_book_for_user(user_id, book_id):
    """Create a checkout row for a user and book."""
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO Checkouts (userID, bookID, out_time, in_time, due_time, fine)
            SELECT %s, %s, CURRENT_TIMESTAMP, NULL, CURRENT_TIMESTAMP + INTERVAL '14 days', 0.00
            WHERE EXISTS (
                SELECT 1
                FROM Books b
                LEFT JOIN Checkouts c ON b.bookID = c.bookID AND c.in_time IS NULL
                WHERE b.bookID = %s
                  AND c.bookID IS NULL
                  AND (b.in_circulation_from IS NULL OR b.in_circulation_from <= CURRENT_DATE)
                  AND (b.in_circulation_until IS NULL OR b.in_circulation_until >= CURRENT_DATE)
            )
            RETURNING due_time
        """, [user_id, book_id, book_id])
        result = cursor.fetchone()
        return result[0] if result else None


def return_book_for_user(user_id, book_id):
    """Mark a user's active checkout as returned and calculate a fine."""
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE Checkouts
            SET in_time = CURRENT_TIMESTAMP,
                fine = CASE
                    WHEN due_time < CURRENT_TIMESTAMP
                    THEN GREATEST(0, FLOOR(EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - due_time)) / 86400) * 0.50)
                    ELSE 0
                END
            WHERE userID = %s
              AND bookID = %s
              AND in_time IS NULL
            RETURNING fine
        """, [user_id, book_id])
        result = cursor.fetchone()
        return result[0] if result else None


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
                   a.first as author_first, a.last as author_last, a.authorID
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


def get_all_books_for_favorites():
    """Get all books available as favorite choices."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT b.bookID, b.name, b.series_name, b.genre,
                   b.authorID, a.first as author_first, a.last as author_last
            FROM Books b
            JOIN Authors a ON b.authorID = a.authorID
            ORDER BY b.name
        """)
        return cursor.fetchall()


def get_all_authors_for_favorites():
    """Get all authors available as favorite choices."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT authorID, first, last, city, country
            FROM Authors
            ORDER BY last, first
        """)
        return cursor.fetchall()


def get_user_favorite_book_ids(user_id):
    """Get IDs for a user's favorite books."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT bookID
            FROM FavoriteBooks
            WHERE userID = %s
        """, [user_id])
        return {row[0] for row in cursor.fetchall()}


def get_user_favorite_author_ids(user_id):
    """Get IDs for a user's favorite authors."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT authorID
            FROM FavoriteAuthors
            WHERE userID = %s
        """, [user_id])
        return {row[0] for row in cursor.fetchall()}


def replace_user_favorites(user_id, book_ids, author_ids):
    """Replace a user's favorite books and authors."""
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM FavoriteBooks WHERE userID = %s", [user_id])
        cursor.execute("DELETE FROM FavoriteAuthors WHERE userID = %s", [user_id])

        for book_id in book_ids:
            cursor.execute("""
                INSERT INTO FavoriteBooks (userID, bookID, authorID)
                SELECT %s, b.bookID, b.authorID
                FROM Books b
                WHERE b.bookID = %s
            """, [user_id, book_id])

        for author_id in author_ids:
            cursor.execute("""
                INSERT INTO FavoriteAuthors (userID, authorID)
                SELECT %s, a.authorID
                FROM Authors a
                WHERE a.authorID = %s
            """, [user_id, author_id])


def add_user_favorite_book(user_id, book_id):
    """Add a single favorite book if it is not already present."""
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO FavoriteBooks (userID, bookID, authorID)
            SELECT %s, b.bookID, b.authorID
            FROM Books b
            WHERE b.bookID = %s
              AND NOT EXISTS (
                  SELECT 1
                  FROM FavoriteBooks fb
                  WHERE fb.userID = %s AND fb.bookID = b.bookID
              )
        """, [user_id, book_id, user_id])


def add_user_favorite_author(user_id, author_id):
    """Add a single favorite author if they are not already present."""
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO FavoriteAuthors (userID, authorID)
            SELECT %s, a.authorID
            FROM Authors a
            WHERE a.authorID = %s
              AND NOT EXISTS (
                  SELECT 1
                  FROM FavoriteAuthors fa
                  WHERE fa.userID = %s AND fa.authorID = a.authorID
              )
        """, [user_id, author_id, user_id])


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
