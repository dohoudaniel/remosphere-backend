from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class UserAdmin(BaseUserAdmin):
    """
    Custom User Admin for User
    Authentication and Authorization
    """
    model = User

    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "is_admin",
        "is_active",
        "email_verified",
        "date_joined",
    )

    list_filter = ("is_admin", "role", "is_active")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("role", "is_admin", "is_active", "email_verified")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": (
                "wide",), "fields": (
                "email", "first_name", "last_name", "password1", "password2"), }, ), )

    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)


admin.site.register(User, UserAdmin)
