# users/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions
from django.conf import settings


class CookieOrHeaderJWTAuthentication(JWTAuthentication):
    """
    Try to authenticate from `Authorization` header first; if missing,
    try to read access token from cookie `JWT_ACCESS_COOKIE_NAME`.
    """

    def authenticate(self, request):
        # 1. Try header auth (parent handles it)
        header_auth = None
        try:
            header_auth = super().authenticate(request)
        except exceptions.AuthenticationFailed:
            # fallthrough to cookie
            header_auth = None

        if header_auth:
            return header_auth

        # 2. Try cookie
        cookie_name = getattr(
            settings,
            "JWT_ACCESS_COOKIE_NAME",
            "remosphere_access")
        raw_token = request.COOKIES.get(cookie_name)
        if not raw_token:
            return None

        try:
            validated = self.get_validated_token(raw_token)
            user = self.get_user(validated)
            return (user, validated)
        except Exception as e:
            raise exceptions.AuthenticationFailed(
                "Invalid token from cookie") from e
