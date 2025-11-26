from rest_framework import serializers
from .models import Job
from categories.models import Category


class JobSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source="created_by.email", read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )
    # category = serializers.PrimaryKeyRelatedField(read_only=False, queryset=None)  # set queryset in view

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "description",
            "category",
            "location",
            "job_type",
            "salary_range",
            "company_name",
            "company",
            "created_by",
            "created_at",
            "updated_at",
            "is_active",
            "slug",
            "expiry_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at", "slug"]
