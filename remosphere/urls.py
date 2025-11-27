"""
URL configuration for remosphere project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

schema_view = get_schema_view(
    openapi.Info(
        title="RemoSphere: Job Board API Docs",
        default_version='v1',
        description="API documentation for RemoSphere",
        contact=openapi.Contact(email="dohoudanielfavour@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Swagger UI
    re_path(
        r'^swagger/$',
        schema_view.with_ui(
            'swagger',
            cache_timeout=0),
        name='schema-swagger-ui'),

    # ReDoc
    re_path(
        r'^redoc/$',
        schema_view.with_ui(
            'redoc',
            cache_timeout=0),
        name='schema-redoc'),

    # Docs
    re_path(
        r'^api/docs/$',
        schema_view.with_ui(
            'swagger',
            cache_timeout=0),
        name='schema-swagger-ui'),
    re_path(
        r'^docs/$',
        schema_view.with_ui(
            'swagger',
            cache_timeout=0),
        name='schema-swagger-ui'),

    # JSON schema view
    re_path(
        r'^swagger.json$',
        schema_view.without_ui(
            cache_timeout=0),
        name='schema-json'),

    # Users
    path("api/users/", include("users.urls")),

    # The job categories
    path('api/', include('categories.urls')),

    # The job applications
    path("api/", include("jobs.urls")),

    # The companies categories
    path('api/', include('companies.urls')),

    # The Authentication
    path("api/auth/", include("authentication.urls")),  # JWT token endpoints,

    # The Applications for user application
    path("api/", include("applications.urls")),


    # path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
