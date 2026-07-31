"""
Custom JWT login that accepts either an email address or a phone number in the
"username" field, delegating to users.backends.EmailOrPhoneBackend.
"""
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class EmailOrPhoneTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Uses the default 'username' field but the value may be an email or phone
    number -- authentication is resolved by EmailOrPhoneBackend in settings."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.get_full_name() or user.username
        token['email'] = user.email
        return token


class EmailOrPhoneTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailOrPhoneTokenObtainPairSerializer
