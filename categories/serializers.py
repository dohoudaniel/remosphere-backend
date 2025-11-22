from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    CategorySerializer

    A Django REST Framework serializer for the Category model.

    Purpose:
    - Serialize and deserialize Category model instances for API endpoints.
    - Ensure only allowed fields are writable by API clients.
    - Provide a consistent format for JSON responses.

    Fields:
    - id: Auto-generated primary key (read-only).
    - name: Human-readable name of the category (required for creation/updating).
    - slug: URL-friendly version of the category name (auto-generated, read-only).
    - description: Optional textual description of the category.
    - created_at: Timestamp when the category was created (read-only).

    Usage:
    - Used in DRF ViewSets or APIViews to handle API requests for categories.
    - Supports CRUD operations while enforcing read-only constraints on certain fields.
    """

    class Meta:
        model = Category
        fields = ["id", "name", "description", "created_at"]
        read_only_fields = ["id", "created_at"]

