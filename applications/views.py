from rest_framework import viewsets, status, permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Application
from .serializers import ApplicationCreateSerializer, ApplicationDetailSerializer
from drf_yasg.utils import swagger_auto_schema


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    Job application management

    - list: authenticated user sees their own applications; admin sees all.
    - create: authenticated user can apply (creates Application).
    - retrieve: owner or admin can view.
    - destroy: owner can withdraw, admin can delete.
    """
    queryset = Application.objects.all()  # select_related("job", "user").all()
    permission_classes = [IsAuthenticated]  # further checks below
    http_method_names = ["get", "post", "delete", "head", "options"]

    @swagger_auto_schema(
        operation_summary="Apply for an available job",
        responses={
            200: "Successfully applied for job application",
            400: "Invalid token",
            404: "Job application not found",
        }
    )
    def get_serializer_class(self):
        if self.action == "create":
            return ApplicationCreateSerializer
        return ApplicationDetailSerializer

    @swagger_auto_schema(
        operation_summary="Search for applied jobs",
        responses={
            200: "Successfully retrieved job applications",
            400: "Invalid token",
            404: "Job application not found",
        }
    )
    def get_queryset(self):
        # Needed so Swagger/OpenAPI schema generation doesn't crash
        if getattr(self, "swagger_fake_view", False):
            return Application.objects.none()

        user = self.request.user

        # normalize admin check
        is_admin = getattr(user, "is_admin", False)

        if is_admin:
            return Application.objects.all()
            # return super().get_queryset()

        if user.is_authenticated:
            return Application.objects.filter(user=user)

        # return super().get_queryset().filter(user=user)
        # anonymous user → return empty queryset (prevents errors)
        return Application.objects.none()

    @swagger_auto_schema(
        operation_summary="Apply for an available job",
        responses={
            200: "Successfully applied for job application",
            400: "Invalid token",
            404: "Job application not found",
        }
    )
    def perform_create(self, serializer):
        # serializer.create will set user from request
        serializer.save()  # .save(user=self.request.user)

    @swagger_auto_schema(
        operation_summary="Delete user application for a job. Only the owner of the application or an admin can delete.",
        responses={
            200: "Withdrawn from job application",
            400: "Invalid token",
            404: "Job application not found",
        })
    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()
        user = request.user
        # only owner or admin can delete
        if not (user.is_admin or instance.user_id == user.id):
            return Response({"detail": "Not allowed."},
                            status=status.HTTP_403_FORBIDDEN)
        # interpret destroy as "withdraw" for owner (set status)
        if instance.user_id == user.id and not user.is_admin:
            instance.status = instance.STATUS_WITHDRAWN
            instance.save(update_fields=["status"])
            return Response({"detail": "Application withdrawn."},
                            status=status.HTTP_200_OK)
        # admin delete
        return super().destroy(request, *args, **kwargs)
