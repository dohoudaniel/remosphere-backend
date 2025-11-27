"""Serializers for authentication flows such as password reset.

These serializers validate input for requesting password resets and
for applying a new password using a reset token.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer accepting an email address for
    password reset requests.
    """
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer that accepts a reset token and new password.
    """
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        # run Django's password validators and return helpful errors
        try:
            password_validation.validate_password(value)
        except Exception as exc:
            # password_validation raises ValidationError, whose messages live
            # in exc.messages
            raise serializers.ValidationError(exc.messages)
        return value
