from django.contrib.auth.backends import BaseBackend
from .models import User


class UserIDBackend(BaseBackend):
    """Authenticate users by their numeric User ID only."""

    def authenticate(self, request, user_id=None, **kwargs):
        if not user_id:
            return None
        try:
            user = User.objects.get(userID=user_id)
        except User.DoesNotExist:
            return None

        if user.is_active:
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
