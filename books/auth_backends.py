from django.contrib.auth.backends import BaseBackend
from django.db import connection
from .models import User


class UserIDBackend(BaseBackend):
    """Authenticate users by their numeric User ID only."""

    def _get_user_by_id(self, user_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT userID, first, last, is_staff, balance, mailing_address, zipcode
                FROM Users
                WHERE userID = %s
            """, [user_id])
            row = cursor.fetchone()

        if not row:
            return None

        user = User(
            userID=row[0],
            first=row[1],
            last=row[2],
            is_staff=row[3],
            balance=row[4],
            mailing_address=row[5],
            zipcode=row[6],
        )
        user.is_active = True
        user.is_superuser = row[3]
        user.username = str(row[0])
        user.backend = 'books.auth_backends.UserIDBackend'
        return user

    def authenticate(self, request, user_id=None, **kwargs):
        if not user_id:
            return None
        return self._get_user_by_id(user_id)

    def get_user(self, user_id):
        return self._get_user_by_id(user_id)
