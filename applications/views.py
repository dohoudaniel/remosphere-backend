from rest_framework import viewsets, status, permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Application
from .serializers import ApplicationCreateSerializer, ApplicationDetailSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    - list: authenticated user sees their own applications; admin sees all.
    - create: authenticated user can apply (creates Application).
    - retrieve: owner or admin can view.
    - destroy: owner can withdraw, admin can delete.
    """
    queryset = Application.objects.all()  # select_related("job", "user").all()
    permission_classes = [IsAuthenticated]  # further checks below
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.action == "create":
            return ApplicationCreateSerializer
        return ApplicationDetailSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return super().get_queryset()
        return super().get_queryset().filter(user=user)

    def perform_create(self, serializer):
        # serializer.create will set user from request
        serializer.save()  # .save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        # only owner or admin can delete
        if not (user.is_admin or instance.user_id == user.id):
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        # interpret destroy as "withdraw" for owner (set status)
        if instance.user_id == user.id and not user.is_admin:
            instance.status = instance.STATUS_WITHDRAWN
            instance.save(update_fields=["status"])
            return Response({"detail": "Application withdrawn."}, status=status.HTTP_200_OK)
        # admin delete
        return super().destroy(request, *args, **kwargs)
