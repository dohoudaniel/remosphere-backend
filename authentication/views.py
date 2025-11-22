from django.conf import settings
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from users.serializers import LoginSerializer, RegisterSerializer, UserSerializer
from .email_utils import make_verification_token, verify_verification_token, send_verification_email
from users.models import User


def set_jwt_cookies(response, access_token, refresh_token):
    cookie_opts = {
        "httponly": getattr(settings, "JWT_COOKIE_HTTPONLY", True),
        "secure": getattr(settings, "JWT_COOKIE_SECURE", False),
        "samesite": getattr(settings, "JWT_COOKIE_SAMESITE", "Lax"),
    }
    access_cookie_name = getattr(settings, "JWT_ACCESS_COOKIE_NAME", "remosphere_access")
    refresh_cookie_name = getattr(settings, "JWT_COOKIE_NAME", "remosphere_refresh")

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
        serializer = LoginSerializer(data=request.data, context={"request": request})
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
        refresh_cookie_name = getattr(settings, "JWT_COOKIE_NAME", "remosphere_refresh")
        refresh_token = request.COOKIES.get(refresh_cookie_name)

        if not refresh_token:
            return Response({"detail": "Refresh token cookie not found"}, status=401)

        try:
            r = RefreshToken(refresh_token)
        except Exception:
            return Response({"detail": "Invalid refresh token"}, status=401)

        new_access = r.access_token
        refresh_str = str(r)
        access_str = str(new_access)

        response = Response({"access": access_str, "refresh": refresh_str}, status=200)
        set_jwt_cookies(response, access_str, refresh_str)
        return response


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Logout user and blacklist refresh token",
        responses={200: "Logged out"}
    )
    def post(self, request):
        refresh_cookie_name = getattr(settings, "JWT_COOKIE_NAME", "remosphere_refresh")
        token = request.COOKIES.get(refresh_cookie_name)

        if token:
            try:
                r = RefreshToken(token)
                r.blacklist()
            except Exception:
                pass

        response = Response({"detail": "Logged out"}, status=200)
        response.delete_cookie(getattr(settings, "JWT_COOKIE_NAME", "remosphere_refresh"))
        response.delete_cookie(getattr(settings, "JWT_ACCESS_COOKIE_NAME", "remosphere_access"))
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

