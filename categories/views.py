from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Category
from .serializers import CategorySerializer

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only admin users to create, update, or delete objects.
    Read-only requests are allowed for any authenticated user.
    """

    def has_permission(self, request, view):
        # SAFE_METHODS = GET, HEAD, OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        # Write permissions are only allowed to admin users
        return request.user and request.user.is_authenticated and request.user.is_admin


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint to manage job categories.

    - List & Retrieve: Any authenticated user
    - Create, Update, Delete: Admin only
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

