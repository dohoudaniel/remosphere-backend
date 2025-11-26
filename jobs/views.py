from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Job
from .serializers import JobSerializer
from .permissions import IsAdminOrReadOnly
from categories.models import Category

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().select_related("category", "company", "created_by")
    serializer_class = JobSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["location", "category"]
    search_fields = ["title", "description", "company_name", "location"]
    ordering_fields = ["created_at", "updated_at", "title"]

    def get_queryset(self):
        qs = super().get_queryset()
        # non-admins only see active jobs
        user = self.request.user
        if not (user.is_authenticated and user.is_staff):
            qs = qs.filter(is_active=True)
        return qs

    def get_serializer(self, *args, **kwargs):
        ser = super().get_serializer(*args, **kwargs)
        # set category queryset dynamically to avoid circular import issues
        ser.fields["category"].queryset = Category.objects.all()
        return ser

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
