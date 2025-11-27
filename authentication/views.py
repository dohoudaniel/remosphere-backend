"""Authentication-related API views and helpers.

Endpoints include login, logout, token refresh, email verification and
password reset flows. This module's edits are limited to documentation
only and do not alter runtime behavior.
"""

from django.conf import settings
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_yasg import openapi
from users.serializers import LoginSerializer, RegisterSerializer, UserSerializer
from .email_utils import make_verification_token, verify_verification_token, send_verification_email, make_password_reset_token, verify_password_reset_token, send_password_reset_email
from users.models import User
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone
from .serializers import ForgotPasswordSerializer, ResetPasswordSerializer
from rest_framework.permissions import AllowAny

User = get_user_model()


def set_jwt_cookies(response, access_token, refresh_token):
    cookie_opts = {
        "httponly": getattr(settings, "JWT_COOKIE_HTTPONLY", True),
        "secure": getattr(settings, "JWT_COOKIE_SECURE", False),
        "samesite": getattr(settings, "JWT_COOKIE_SAMESITE", "Lax"),
    }
    access_cookie_name = getattr(
        settings,
        "JWT_ACCESS_COOKIE_NAME",
        "remosphere_access")
    refresh_cookie_name = getattr(
        settings,
        "JWT_COOKIE_NAME",
        "remosphere_refresh")

    response.set_cookie(access_cookie_name, access_token, **cookie_opts)
    response.set_cookie(refresh_cookie_name, refresh_token, **cookie_opts)
    return response


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Login user and return JWT tokens",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "access": openapi.Schema(type=openapi.TYPE_STRING),
                        "refresh": openapi.Schema(type=openapi.TYPE_STRING),
                        "user": openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            400: "Invalid credentials"
        }
    )
    def post(self, request):
        serializer = LoginSerializer(
            data=request.data, context={
                "request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.context.get("user")

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        response = Response(
            {
                "message": "Login successful",
                "access": str(access),
                "refresh": str(refresh),
                "user": serializer.get_user(None),
            },
            status=status.HTTP_200_OK,
        )
        set_jwt_cookies(response, str(access), str(refresh))
        return response


class CookieTokenRefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Refresh JWT tokens from HttpOnly cookie",
        responses={
            200: openapi.Response(
                description="Tokens refreshed",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "access": openapi.Schema(type=openapi.TYPE_STRING),
                        "refresh": openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            401: "Invalid or missing refresh token"
        }
    )
    def post(self, request):
        refresh_cookie_name = getattr(
            settings, "JWT_COOKIE_NAME", "remosphere_refresh")
        refresh_token = request.COOKIES.get(refresh_cookie_name)

        if not refresh_token:
            return Response(
                {"detail": "Refresh token cookie not found"}, status=401)

        try:
            r = RefreshToken(refresh_token)
        except Exception:
            return Response({"detail": "Invalid refresh token"}, status=401)

        new_access = r.access_token
        refresh_str = str(r)
        access_str = str(new_access)

        response = Response(
            {"access": access_str, "refresh": refresh_str}, status=200)
        set_jwt_cookies(response, access_str, refresh_str)
        return response


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Logout user and blacklist refresh token",
        responses={200: "Logged out"}
    )
    def post(self, request):
        refresh_cookie_name = getattr(
            settings, "JWT_COOKIE_NAME", "remosphere_refresh")
        token = request.COOKIES.get(refresh_cookie_name)

        if token:
            try:
                r = RefreshToken(token)
                r.blacklist()
            except Exception:
                pass

        response = Response({"detail": "Logged out"}, status=200)
        response.delete_cookie(
            getattr(
                settings,
                "JWT_COOKIE_NAME",
                "remosphere_refresh"))
        response.delete_cookie(
            getattr(
                settings,
                "JWT_ACCESS_COOKIE_NAME",
                "remosphere_access"))
        return response


class RequestVerificationView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Send email verification link",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=["email"]
        ),
        responses={200: "Verification email sent", 404: "User not found"}
    )
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email required"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "No user with that email"}, status=404)

        send_verification_email(user, request=request)
        return Response({"detail": "Verification email sent"}, status=200)


class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Verify user email via token",
        responses={
            200: "Email verified",
            400: "Invalid token",
            404: "User not found",
        }
    )
    def get(self, request):
        token = request.query_params.get("token")
        if not token:
            return Response({"detail": "token required"}, status=400)

        email = verify_verification_token(token)
        if not email:
            return Response({"detail": "Invalid or expired token"}, status=400)

        try:
            user = User.objects.get(email=email)
            user.email_verified = True
            user.save(update_fields=["email_verified"])
            return Response({"detail": "Email verified"}, status=200)

        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=404)


def _rate_limit_key_email(email):
    return f"pwreset:email:{email}"


def _rate_limit_key_ip(ip):
    return f"pwreset:ip:{ip}"


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        # method="post",
        operation_description="Request a password reset email.",
        request_body=ForgotPasswordSerializer,
        responses={
            200: openapi.Response("Success", schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(type=openapi.TYPE_STRING)
                }
            )),
            429: "Too many requests",
        },
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower().strip()

        # Rate limiting per email
        email_key = _rate_limit_key_email(email)
        email_count = cache.get(email_key, 0)
        if email_count >= getattr(
            settings,
            "PASSWORD_RESET_RATE_LIMIT_PER_HOUR",
                5):
            return Response(
                {
                    "detail": "Too many password reset requests for this email. Try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Rate limiting per IP
        ip = request.META.get("REMOTE_ADDR", "unknown")
        ip_key = _rate_limit_key_ip(ip)
        ip_count = cache.get(ip_key, 0)
        if ip_count >= getattr(
            settings,
            "PASSWORD_RESET_RATE_LIMIT_IP_PER_HOUR",
                20):
            return Response(
                {
                    "detail": "Too many requests from your IP. Try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS)

        # update counters (expire after 1 hour)
        cache.set(email_key, email_count + 1, timeout=3600)
        cache.set(ip_key, ip_count + 1, timeout=3600)

        # Find user (do not reveal whether email exists in response)
        user = User.objects.filter(email__iexact=email).first()
        if user:
            # create token
            token = make_password_reset_token(user.id)

            # build domain from request (ensure trailing slash for base)
            base = request.build_absolute_uri(
                "/")  # e.g. http://127.0.0.1:8000/
            # queue async sending (pass primitives)
            send_password_reset_email.delay(
                # remove trailing slash for build
                user.email, token, base.rstrip("/"))

        # Always return same generic response for privacy
        return Response(
            {
                "detail": "If an account with that email exists, a password reset link has been sent."},
            status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        # method="post",
        operation_description="Use a valid password reset token to set a new password.",
        request_body=ResetPasswordSerializer,
        responses={
            200: "Password reset successful",
            400: "Invalid or expired token",
        },
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        # verify token
        result = verify_password_reset_token(token)
        if isinstance(result, dict) and result.get("error"):
            err = result["error"]
            if err == "expired":
                return Response({"detail": "Reset link expired."},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": "Invalid reset token."},
                            status=status.HTTP_400_BAD_REQUEST)

        user_id = result.get("user_id")
        if not user_id:
            return Response({"detail": "Invalid reset token."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."},
                            status=status.HTTP_404_NOT_FOUND)

        # Set new password (use set_password to hash)
        user.set_password(new_password)
        # Optionally update last_login/password_changed timestamp if you have it
        # user.password_changed_at = timezone.now()
        user.save(update_fields=["password"])

        # Blacklist outstanding refresh tokens for the user (if token_blacklist
        # app is enabled)
        try:
            from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
            tokens = OutstandingToken.objects.filter(user=user)
            for t in tokens:
                # wrap in try because may already be blacklisted
                try:
                    BlacklistedToken.objects.get_or_create(token=t)
                except Exception:
                    pass
        except Exception:
            # token blacklisting not available/configured — ignore
            pass

        return Response(
            {"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)
