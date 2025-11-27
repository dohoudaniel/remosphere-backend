from rest_framework import serializers
from .models import Job
from categories.models import Category
from companies.models import Company


class JobSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(
        source="created_by.email", read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )

    class Meta:
        model = Job
        fields = "__all__"

        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "updated_at",
            "slug"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # safe dynamic querysets
        self.fields["category"].queryset = Category.objects.all()
        self.fields["company"].queryset = Company.objects.all()
