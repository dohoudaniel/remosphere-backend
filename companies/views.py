from rest_framework import viewsets
# from rest_framework.permissions import IsAuthenticated

from .models import Company
from .serializers import CompanySerializer
from users.permissions import IsAdminOrReadOnly


class CompanyViewSet(viewsets.ModelViewSet):
    """
    Company Management and Tracking for posted jobs

    Admin → Full CRUD
    Authenticated Users → Read-only
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAdminOrReadOnly]
