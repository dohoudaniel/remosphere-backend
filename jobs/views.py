from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import Job
from .serializers import JobSerializer
# from .permissions import IsAdminOrReadOnly
from categories.models import Category
from users.permissions import IsAdminOrReadOnly
from .filters import JobFilter
from django.db.models import Count


class JobViewSet(viewsets.ModelViewSet):
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



