from rest_framework import serializers
from .models import Job
from categories.models import Category
from companies.models import Company


class JobSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(
        source="created_by.email", read_only=True
    )

    # readable names
    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )
    company_name = serializers.CharField(
        source="company.name",
        read_only=True
    )

    class Meta:
        model = Job
        fields = "__all__"

        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "updated_at",
            "slug",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Safe dynamic querysets for browsable API
        if "category" in self.fields:
            self.fields["category"].queryset = Category.objects.all()

        if "company" in self.fields:
            self.fields["company"].queryset = Company.objects.all()
