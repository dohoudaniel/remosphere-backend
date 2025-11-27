from django.urls import path
from .views import RequestVerificationView, VerifyEmailView  # LoginView, LogoutView,,
from .views import ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path(
        "request-verification/",
        RequestVerificationView.as_view(),
        name="request_verification"),

    path(
        "verify-email/",
        VerifyEmailView.as_view(),
        name="email_verify"),

    path(
        "forgot-password/",
        ForgotPasswordView.as_view(),
        name="forgot_password"),

    path(
        "reset-password/",
        ResetPasswordView.as_view(),
        name="reset_password"),
]
