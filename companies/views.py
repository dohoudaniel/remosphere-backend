from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# from rest_framework.permissions import IsAuthenticated

from .models import Company
from .serializers import CompanySerializer
from users.permissions import IsAdminOrReadOnly


class CompanyViewSet(viewsets.ModelViewSet):
    """
    Company management.
    
    Admin → Full CRUD
    Authenticated Users → Read-only
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAdminOrReadOnly]

    @swagger_auto_schema(
        operation_id="list_companies",
        operation_summary="List all companies",
        operation_description="Retrieve a list of all registered companies. Available to all authenticated users.",
        security=[{"JWTAuth": []}],
        responses={
            200: "List of companies",
            401: "Authentication required"
        },
        tags=["Companies"]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="create_company",
        operation_summary="Create a new company",
        operation_description="Create a new company profile. Only available to admin users.",
        security=[{"JWTAuth": []}],
        request_body=CompanySerializer,
        responses={
            201: "Company created successfully",
            400: "Validation error",
            401: "Authentication required",
            403: "Admin permissions required"
        },
        tags=["Companies"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="retrieve_company",
        operation_summary="Retrieve a specific company",
        operation_description="Get details of a specific company by ID.",
        security=[{"JWTAuth": []}],
        responses={
            200: "Company details",
            401: "Authentication required",
            404: "Company not found"
        },
        tags=["Companies"]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="update_company",
        operation_summary="Update a company",
        operation_description="Update an existing company profile. Only available to admin users.",
        security=[{"JWTAuth": []}],
        request_body=CompanySerializer,
        responses={
            200: CompanySerializer,
            400: "Validation error",
            401: "Authentication required",
            403: "Admin permissions required",
            404: "Company not found"
        },
        tags=["Companies"]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="partial_update_company",
        operation_summary="Partially update a company",
        operation_description="Partially update an existing company profile. Only available to admin users.",
        security=[{"JWTAuth": []}],
        request_body=CompanySerializer,
        responses={
            200: CompanySerializer,
            400: "Validation error",
            401: "Authentication required",
            403: "Admin permissions required",
            404: "Company not found"
        },
        tags=["Companies"]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="delete_company",
        operation_summary="Delete a company",
        operation_description="Delete an existing company profile. Only available to admin users.",
        security=[{"JWTAuth": []}],
        responses={
            204: "Company deleted successfully",
            401: "Authentication required",
            403: "Admin permissions required",
            404: "Company not found"
        },
        tags=["Companies"]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
