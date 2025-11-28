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


class RegisterView(generics.CreateAPIView):
    """
    The User Sign Up View
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Register a new user",
        request_body=RegisterSerializer,
        responses={201: "User created"}
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
    """
    Requesting Verification as a User
    """
    permission_classes = [AllowAny]

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
    """
    The User Login view
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Login and receive access + refresh tokens",
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
    """
    The functionality to verify user's email
by sending a verification email to them.
    """
    permission_classes = [AllowAny]

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
    """
    The User Logout functionality.
    It blacklists existing cookies, and
    signs out the user.
    """
    permission_classes = [IsAuthenticated]

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


class CurrentUserView(APIView):
    """
    Get the current authenticated user's details
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get current user details",
        responses={
            200: openapi.Response(
                description="Current user details",
                schema=UserSerializer
            )
        }
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
