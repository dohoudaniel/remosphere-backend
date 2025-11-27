from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    """
    The User Serializer Class
    """
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_admin",
            "email_verified",
            "date_joined",
            "last_login",
        ]
        read_only_fields = [
            "id", "is_admin", "email_verified", "date_joined", "last_login"
        ]


class RegisterSerializer(serializers.ModelSerializer):
    """
    The User Sign up serializer
    """
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "password",
        ]

    def validate_password(self, value):
        try:
            validate_password(value)
        except Exception as e:
            raise serializers.ValidationError(list(e.messages))

        return value

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
        )


class LoginSerializer(serializers.Serializer):
    """
    The User Login serializer
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = serializers.SerializerMethodField(read_only=True)

    def get_user(self, obj):
        user = self.context.get("user")
        if user:
            return UserSerializer(user).data
        return None

    def validate(self, data):
        """
        Validates if user's details exists
        """
        email = data.get("email")
        password = data.get("password")

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password")

        if not user.email_verified:
            raise AuthenticationFailed(
                "Email is not verified. Please verify to continue.")

        refresh = RefreshToken.for_user(user)

        self.context["user"] = user

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
