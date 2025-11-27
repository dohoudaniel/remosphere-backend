from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
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
