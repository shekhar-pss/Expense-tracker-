from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class EmailOrPhoneBackend(ModelBackend):
    """Allow users to authenticate using their email address OR phone number."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email') or kwargs.get('phone')
        if username is None or password is None:
            return None

        try:
            user = User.objects.get(
                Q(email__iexact=username) | Q(profile__phone=username) | Q(username__iexact=username)
            )
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            user = User.objects.filter(
                Q(email__iexact=username) | Q(profile__phone=username) | Q(username__iexact=username)
            ).first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
