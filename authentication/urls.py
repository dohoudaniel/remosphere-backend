from django.urls import path
from .views import LoginView, CookieTokenRefreshView, LogoutView, RequestVerificationView, VerifyEmailView
from rest_framework_simplejwt.views import TokenVerifyView, TokenObtainPairView, TokenRefreshView
from .views import ForgotPasswordView, ResetPasswordView

urlpatterns = [
    # path("login/", LoginView.as_view(), name="token_obtain_pair"),
    path("refresh/", CookieTokenRefreshView.as_view(), name="token_refresh_cookie"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # path("verify/", TokenVerifyView.as_view(), name="token_verify"),
    # path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("request-verification/", RequestVerificationView.as_view(), name="request_verification"),
    path("verify-email/", VerifyEmailView.as_view(), name="email_verify"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
]

