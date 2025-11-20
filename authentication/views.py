from django.conf import settings
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.views import TokenRefreshView
from users.serializers import LoginSerializer, RegisterSerializer
from rest_framework import status, permissions
from .email_utils import make_verification_token, verify_verification_token, send_verification_email
from users.models import User

# helper to set cookies
def set_jwt_cookies(response, access_token, refresh_token):
    # cookie options
    cookie_opts = {
        "httponly": getattr(settings, "JWT_COOKIE_HTTPONLY", True),
        "secure": getattr(settings, "JWT_COOKIE_SECURE", False),
        "samesite": getattr(settings, "JWT_COOKIE_SAMESITE", "Lax"),
        # optionally you can set 'path' and 'max_age' if needed
    }
    access_cookie_name = getattr(settings, "JWT_ACCESS_COOKIE_NAME", "remosphere_access")
    refresh_cookie_name = getattr(settings, "JWT_COOKIE_NAME", "remosphere_refresh")

    # set HttpOnly cookies
    # access token cookie might be short lived (or you can choose to not set it)
    response.set_cookie(access_cookie_name, access_token, **cookie_opts)
    response.set_cookie(refresh_cookie_name, refresh_token, **cookie_opts)

    return response

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.context.get("user")
        # create tokens using Simple JWT
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        resp_body = {
            "message": "Login successful",
            "access": str(access),
            "refresh": str(refresh),
            "user": serializer.get_user(None),
        }

        response = Response(resp_body, status=status.HTTP_200_OK)
        set_jwt_cookies(response, str(access), str(refresh))
        return response


class CookieTokenRefreshView(APIView):
    """
    Refresh endpoint that reads refresh token from HttpOnly cookie and returns new tokens; it
    also rotates refresh token if ROTATE_REFRESH_TOKENS=True.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_cookie_name = getattr(settings, "JWT_COOKIE_NAME", "remosphere_refresh")
        refresh_token = request.COOKIES.get(refresh_cookie_name)
        if refresh_token is None:
            return Response({"detail": "Refresh token cookie not found"}, status=401)

        try:
            r = RefreshToken(refresh_token)
        except Exception:
            return Response({"detail": "Invalid refresh token"}, status=401)

        # blacklisting handled automatically if setting BLACKLIST_AFTER_ROTATION True
        new_access = r.access_token
        # optionally rotate refresh token:
        if getattr(settings, "SIMPLE_JWT", {}).get("ROTATE_REFRESH_TOKENS", False):
            r.blacklist()
            new_r = RefreshToken.for_user(r.user)
            refresh_str = str(new_r)
            access_str = str(new_access)
        else:
            refresh_str = str(r)
            access_str = str(new_access)

        response = Response({
            "access": access_str,
            "refresh": refresh_str,
        }, status=200)

        set_jwt_cookies(response, access_str, refresh_str)
        return response


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # get refresh token from cookie, blacklist it
        refresh_cookie_name = getattr(settings, "JWT_COOKIE_NAME", "remosphere_refresh")
        token = request.COOKIES.get(refresh_cookie_name)
        if token:
            try:
                r = RefreshToken(token)
                r.blacklist()
            except Exception:
                pass

        # clear cookies
        response = Response({"detail": "Logged out"}, status=status.HTTP_200_OK)
        response.delete_cookie(getattr(settings, "JWT_COOKIE_NAME", "remosphere_refresh"))
        response.delete_cookie(getattr(settings, "JWT_ACCESS_COOKIE_NAME", "remosphere_access"))
        return response


class RequestVerificationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email required"}, status=400)
        # if user exists, send verification email (or create a temporary pending record)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "No user with that email"}, status=404)

        send_verification_email(user, request=request)
        return Response({"detail": "Verification email sent"}, status=200)


class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]
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
