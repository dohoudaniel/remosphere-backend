from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
)
from rest_framework.permissions import AllowAny


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.context.get("user")

        return Response(
            {
                "message": "Login successful",
                "access": serializer.validated_data["access"],
                "refresh": serializer.validated_data["refresh"],
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK
        )
