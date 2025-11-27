from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Job
from .serializers import JobSerializer
# from .permissions import IsAdminOrReadOnly
from categories.models import Category
from users.permissions import IsAdminOrReadOnly
from .filters import JobFilter
from django.db.models import Count


class JobViewSet(viewsets.ModelViewSet):
    """
    Job listings management.
    
    - List & Retrieve: All authenticated users (only active jobs for non-admins)
    - Create, Update, Delete: Admin only
    - Supports filtering, searching, and ordering
    """
    # .order_by("-created_at")  # .select_related("category", "company", "created_by")
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAdminOrReadOnly]  # [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter]
    filterset_class = JobFilter

    # filterset_fields = ["location", "category"]
    # search_fields = ["title", "description", "company_name", "category_name", "location"]

    search_fields = [
        "title",
        "description",
        "category__name",   # search by category name
        "company_name",    # search by company name
        "location",
        "job_type",
    ]

    # EXACT FILTER FIELDS
    filterset_fields = [
        "category__name",
        "company_name",
        "location",
        "job_type",
        "is_active",
    ]

    ordering_fields = ["created_at", "updated_at", "title"]

    @swagger_auto_schema(
        operation_id="list_jobs",
        operation_summary="List all job postings",
        operation_description="Retrieve a paginated list of job postings. Supports filtering by category, location, job type, and full-text search. Non-admin users only see active jobs.",
        security=[{"JWTAuth": []}],
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search in title, description, category, company name, and location",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                "category__name",
                openapi.IN_QUERY,
                description="Filter by category name",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                "company_name",
                openapi.IN_QUERY,
                description="Filter by company name",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                "location",
                openapi.IN_QUERY,
                description="Filter by job location",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                "job_type",
                openapi.IN_QUERY,
                description="Filter by job type (full_time, part_time, contract, etc.)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                "is_active",
                openapi.IN_QUERY,
                description="Filter by active status (admin only)",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="Order by field (created_at, updated_at, title). Prefix with '-' for descending",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: "List of jobs with pagination",
            401: "Authentication required"
        },
        tags=["Jobs"]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="create_job",
        operation_summary="Create a new job posting",
        operation_description="Create a new job posting. Only available to admin users.",
        security=[{"JWTAuth": []}],
        request_body=JobSerializer,
        responses={
            201: "Job created successfully",
            400: "Validation error",
            401: "Authentication required",
            403: "Admin permissions required"
        },
        tags=["Jobs"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="retrieve_job",
        operation_summary="Retrieve a specific job",
        operation_description="Get detailed information about a specific job posting including application count.",
        security=[{"JWTAuth": []}],
        responses={
            200: "Job details",
            401: "Authentication required",
            404: "Job not found"
        },
        tags=["Jobs"]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="update_job",
        operation_summary="Update a job posting",
        operation_description="Update an existing job posting. Only available to admin users.",
        security=[{"JWTAuth": []}],
        request_body=JobSerializer,
        responses={
            200: JobSerializer,
            400: "Validation error",
            401: "Authentication required",
            403: "Admin permissions required",
            404: "Job not found"
        },
        tags=["Jobs"]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="partial_update_job",
        operation_summary="Partially update a job posting",
        operation_description="Partially update an existing job posting. Only available to admin users.",
        security=[{"JWTAuth": []}],
        request_body=JobSerializer,
        responses={
            200: JobSerializer,
            400: "Validation error",
            401: "Authentication required",
            403: "Admin permissions required",
            404: "Job not found"
        },
        tags=["Jobs"]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="delete_job",
        operation_summary="Delete a job posting",
        operation_description="Delete an existing job posting. Only available to admin users.",
        security=[{"JWTAuth": []}],
        responses={
            204: "Job deleted successfully",
            401: "Authentication required",
            403: "Admin permissions required",
            404: "Job not found"
        },
        tags=["Jobs"]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        qs = Job.objects.all().annotate(
            applications_count=Count("applications__user", distinct=True)
        )
        # qs = super().get_queryset()
        # non-admins only see active jobs
        user = self.request.user
        if not (user.is_authenticated):  # and user.is_staff):
            qs = qs.filter(is_active=True)
        return qs


    def get_serializer(self, *args, **kwargs):
        ser = super().get_serializer(*args, **kwargs)
        # set category queryset dynamically to avoid circular import issues

        # Only modify serializer when it is NOT a ListSerializer
        if hasattr(ser, "fields"):
            ser.fields["category"].queryset = Category.objects.all()

        return ser

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)



