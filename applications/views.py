from rest_framework import viewsets, status, permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from .models import Application
from .serializers import ApplicationCreateSerializer, ApplicationDetailSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    Job application management.
    
    - list: authenticated user sees their own applications; admin sees all.
    - create: authenticated user can apply (creates Application).
    - retrieve: owner or admin can view.
    - destroy: owner can withdraw, admin can delete.
    """
    queryset = Application.objects.all()  # select_related("job", "user").all()
    permission_classes = [IsAuthenticated]  # further checks below
    http_method_names = ["get", "post", "delete", "head", "options"]

    @swagger_auto_schema(
        operation_id="list_applications",
        operation_summary="List job applications",
        operation_description="List applications. Regular users see only their own applications, admins see all.",
        security=[{"JWTAuth": []}],
        responses={
            200: "List of applications",
            401: "Authentication required"
        },
        tags=["Applications"]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="create_application",
        operation_summary="Apply for a job",
        operation_description="Submit an application for a job posting. User can only have one application per job.",
        security=[{"JWTAuth": []}],
        request_body=ApplicationCreateSerializer,
        responses={
            201: "Application submitted successfully",
            400: "Validation error or duplicate application",
            401: "Authentication required",
            404: "Job not found"
        },
        tags=["Applications"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="retrieve_application",
        operation_summary="Retrieve application details",
        operation_description="Get detailed information about a specific application. Users can only view their own applications, admins can view all.",
        security=[{"JWTAuth": []}],
        responses={
            200: "Application details",
            401: "Authentication required",
            403: "Permission denied",
            404: "Application not found"
        },
        tags=["Applications"]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="withdraw_application",
        operation_summary="Withdraw/Delete application",
        operation_description="Withdraw an application (sets status to withdrawn for user) or delete it (admin only).",
        security=[{"JWTAuth": []}],
        responses={
            200: openapi.Response(
                description="Application withdrawn",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Withdrawal confirmation message"
                        )
                    }
                )
            ),
            204: "Application deleted (admin)",
            401: "Authentication required",
            403: "Permission denied",
            404: "Application not found"
        },
        tags=["Applications"]
    )
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

    def get_serializer_class(self):
        if self.action == "create":
            return ApplicationCreateSerializer
        return ApplicationDetailSerializer

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
