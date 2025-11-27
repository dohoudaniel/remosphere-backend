from django.shortcuts import render
from rest_framework import viewsets, permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Category
from .serializers import CategorySerializer
from users.permissions import IsAdminOrReadOnly

# class IsAdminOrReadOnly(permissions.BasePermission):
#     """
#     Custom permission to allow only admin users to create, update, or delete objects.
#     Read-only requests are allowed for any authenticated user.
#     """

#     def has_permission(self, request, view):
#         # SAFE_METHODS = GET, HEAD, OPTIONS
#         if request.method in permissions.SAFE_METHODS:
#             return request.user and request.user.is_authenticated
#         # Write permissions are only allowed to admin users
# return request.user and request.user.is_authenticated and
# request.user.is_admin


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint to manage job categories.

    - List & Retrieve: Any authenticated user
    - Create, Update, Delete: Admin only
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    @swagger_auto_schema(
        operation_id="list_categories",
        operation_summary="List all job categories",
        operation_description="Retrieve a list of all available job categories. Available to all authenticated users.",
        security=[{"JWTAuth": []}],
        responses={
            200: openapi.Response(
                description="List of categories",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "name": openapi.Schema(type=openapi.TYPE_STRING),
                            "description": openapi.Schema(type=openapi.TYPE_STRING),
                            "created_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
                        }
                    )
                )
            ),
            401: "Authentication required"
        },
        tags=["Categories"]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="create_category",
        operation_summary="Create a new job category",
        operation_description="Create a new job category. Only available to admin users.",
        security=[{"JWTAuth": []}],
        request_body=CategorySerializer,
        responses={
            201: openapi.Response(
                description="Category created successfully",
                schema=CategorySerializer
            ),
            400: "Validation error",
            401: "Authentication required",
            403: "Admin permissions required"
        },
        tags=["Categories"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="retrieve_category",
        operation_summary="Retrieve a specific category",
        operation_description="Get details of a specific job category by ID.",
        security=[{"JWTAuth": []}],
        responses={
            200: CategorySerializer,
            401: "Authentication required",
            404: "Category not found"
        },
        tags=["Categories"]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="update_category",
        operation_summary="Update a job category",
        operation_description="Update an existing job category. Only available to admin users.",
        security=[{"JWTAuth": []}],
        request_body=CategorySerializer,
        responses={
            200: CategorySerializer,
            400: "Validation error",
            401: "Authentication required",
            403: "Admin permissions required",
            404: "Category not found"
        },
        tags=["Categories"]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="partial_update_category",
        operation_summary="Partially update a job category",
        operation_description="Partially update an existing job category. Only available to admin users.",
        security=[{"JWTAuth": []}],
        request_body=CategorySerializer,
        responses={
            200: CategorySerializer,
            400: "Validation error",
            401: "Authentication required",
            403: "Admin permissions required",
            404: "Category not found"
        },
        tags=["Categories"]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="delete_category",
        operation_summary="Delete a job category",
        operation_description="Delete an existing job category. Only available to admin users.",
        security=[{"JWTAuth": []}],
        responses={
            204: "Category deleted successfully",
            401: "Authentication required",
            403: "Admin permissions required",
            404: "Category not found"
        },
        tags=["Categories"]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
