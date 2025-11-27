from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from django.conf import settings
from users.models import User


class CookieJWTAuthentication(BaseAuthentication):
    """
    """
    def authenticate(self, request):
        """
        """
        access_token = request.COOKIES.get("access_token")

        if not access_token:
            return None   # No token → DRF will move to next auth backend

        try:
            validated_token = AccessToken(access_token)
            user_id = validated_token.get("user_id")
            user = User.objects.filter(id=user_id).first()

            if user:
                return (user, None)
            return None

        except Exception:
            raise AuthenticationFailed("Invalid or expired access token")
