"""
User-facing API views.

This module exposes registration, login, email verification and
logout endpoints used by the frontend. Only documentation strings
and inline comments are added here — no behavioral changes.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from rest_framework.views import APIView
from authentication.email_utils import send_welcome_email, send_verification_email
from .models import User
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import IntegrityError
from rest_framework import serializers
import logging

logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    """
    Handle user registration requests.

    The `post` method validates input and creates a user record,
    then queues an email verification task via Celery.
    """

    @swagger_auto_schema(
        operation_id="register_user",
        operation_summary="Register a new user",
        operation_description="Create a new user account and send email verification. User must verify email before being able to login.",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="User registration successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Registration success message"
                        )
                    }
                )
            ),
            400: openapi.Response(
                description="Validation error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "field_name": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="Field validation errors"
                        )
                    }
                )
            )
        },
        tags=["Authentication"]
    )
    def post(self, request, *args, **kwargs):
        # Use serializer to create the user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # <-- user is now created

        # Use request to dynamically build the domain
        domain = request.build_absolute_uri("/").rstrip("/")

        # Queue the verification email using Celery
        send_verification_email.delay(user.id, domain)

        return Response(
            {
                "detail": "User successfully signed up. Please check your email for verification."
            },
            status=201
        )
        # return super().post(request, *args, **kwargs)

    def create(self, validated_data):
        try:
            user = User.objects.create_user(**validated_data)
            return user
        except IntegrityError as e:
            if "unique constraint" in str(e):
                raise serializers.ValidationError(
                    {"email": "A user with this email already exists."})
            # raise e


class RequestVerificationEmailView(APIView):
    permission_classes = [AllowAny]
    """
    Endpoint to request resending of verification emails.
    """

    @swagger_auto_schema(
        operation_id="request_verification_email",
        operation_summary="Request email verification resend",
        operation_description="Resend verification email to user. Can be used by authenticated user or with email parameter.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description="Email address to send verification to (required if not authenticated)"
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Verification email sent",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "User already verified or bad request",
            404: "User not found"
        },
        tags=["Authentication"]
    )
    def post(self, request):
        user = request.user if request.user.is_authenticated else None
        email = request.data.get("email")

        if user is None and email:
            user = User.objects.filter(email=email).first()

        if user is None:
            return Response({"detail": "User not found"}, status=404)

        if user.is_email_verified:
            return Response(
                {"detail": "User has already verified email"},
                status=400
            )

        send_verification_email(user)
        return Response({"detail": "Verification email sent"})


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    """
    Authenticate user credentials and
    return tokens + set cookies.
    """

    @swagger_auto_schema(
        operation_id="login_user",
        operation_summary="Login and receive access + refresh tokens",
        operation_description="Authenticate user with email/password and return JWT tokens. Also sets HttpOnly cookies for token storage.",
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
            )
        }
    )
    def post(self, request, *args, **kwargs):
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # user = serializer.context.get("user")

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # user = serializer.validated_data["user"]
        user = serializer.context.get("user")
        access_token = serializer.validated_data["access"]
        refresh_token = serializer.validated_data["refresh"]

        response = Response(
            {
                "message": "Login successful",
                "access": serializer.validated_data["access"],
                "refresh": serializer.validated_data["refresh"],
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK
        )

        # 2️⃣ Set HttpOnly Cookies
        response.set_cookie(
            "access_token",
            access_token,
            httponly=True,
            secure=settings.JWT_COOKIE_SECURE,
            samesite=settings.JWT_COOKIE_SAMESITE,
        )

        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            secure=settings.JWT_COOKIE_SECURE,
            samesite=settings.JWT_COOKIE_SAMESITE,
        )

        return response


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    """
    Verify an email address using a token provided in the URL.
    """

    @swagger_auto_schema(
        operation_id="verify_email",
        operation_summary="Verify user email address",
        operation_description="Verify user email using token from verification email. Sets email_verified to True.",
        manual_parameters=[
            openapi.Parameter(
                "token",
                openapi.IN_PATH,
                description="Email verification token",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Email verified successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Verification success message"
                        )
                    }
                )
            ),
            400: "Invalid or expired token"
        },
        tags=["Authentication"]
    )
    def get(self, request, token):
        user = verify_token(token)  # You already have this func

        if user is None:
            return Response({"detail": "Invalid or expired token"}, status=400)

        if user.is_email_verified:
            return Response({"detail": "Email already verified"}, status=200)

        user.is_email_verified = True
        user.save()

        # send_welcome_email(user)
        try:
            # send_welcome_email.delay(user.email)
            return Response(
                {"detail": "Email verified successfully"}, status=200)

        except Exception as e:
            logger.error(f"Error sending confirmation email: {e}")
            return Response(
                {"message": "Email verified, but confirmation email failed."}, status=status.HTTP_200_OK)

        # return Response({"detail": "Email verified successfully"},
        # status=200)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    """
    Logout endpoint that blacklists
    refresh tokens and clears cookies.
    """

    @swagger_auto_schema(
        operation_id="logout_user",
        operation_summary="Logout user",
        operation_description="Logout user by blacklisting refresh token and clearing authentication cookies.",
        security=[{"JWTAuth": []}],
        responses={
            200: openapi.Response(
                description="Successfully logged out",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Logout success message"
                        )
                    }
                )
            ),
            401: "Authentication required"
        },
        tags=["Authentication"]
    )
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            response = Response(
                {"detail": "Logged out."},
                status=status.HTTP_200_OK
            )
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            return response

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()   # <-- This is the server invalidation
        except Exception:
            pass

        response = Response(
            {"detail": "Logged out successfully"},
            status=status.HTTP_200_OK
        )

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response
