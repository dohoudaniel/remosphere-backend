"""Users models.

Contains the custom `User` model and `UserManager`.
These docstrings and inline comments are non-functional and
are intended to improve code readability for contributors.
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    """Manager for `User` model that provides user creation helpers.

    This mirrors Django's recommended pattern for custom user models.
    """

    def create_user(
            self,
            email,
            first_name,
            last_name,
            password=None,
            **extra_fields):
        """Create and return a `User` with the given email and names.

        Raises:
            ValueError: If `email` is not provided.
        """
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)

        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            # username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
            self,
            email,
            first_name,
            last_name,
            password=None,
            **extra_fields):
        """Create and return a superuser (admin role).

        Ensures `is_admin` and `role` defaults are set.
        """
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("role", "admin")
        # Accept username to avoid TypeError
        # extra_fields.setdefault("username", "")
        return self.create_user(
            email,
            first_name,
            last_name,
            password,
            **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model using email for authentication.

    Attributes reflect profile information and verification state.
    """
    email = models.EmailField(unique=True, db_index=True)
    # username = models.CharField(max_length=50, unique=True)  #
    # firstname+lastname
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    role = models.CharField(max_length=50, default="user")  # 'admin' or 'user'
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    email_verified = models.BooleanField(default=False, db_index=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email

    @property
    def username(self):
        """
        Combine first and last name for display purposes.
        """
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if self.pk:
            old = User.objects.get(pk=self.pk)
            self._previous_is_verified = old.email_verified
        else:
            self._previous_is_verified = False

        super().save(*args, **kwargs)