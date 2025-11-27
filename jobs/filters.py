import django_filters
from .models import Job


class JobFilter(django_filters.FilterSet):
    """
    The search and filtering functionality for jobs by:

    - location
    - job type
    - category
    - activeness
    - company name
    - a search string
    """
    category_name = django_filters.CharFilter(
        field_name="category__name",
        lookup_expr="icontains"
    )

    company_display_name = django_filters.CharFilter(
        field_name="company__name",
        lookup_expr="icontains"
    )

    job_type = django_filters.CharFilter(
        lookup_expr="iexact"
    )

    location = django_filters.CharFilter(
        lookup_expr="icontains"
    )

    class Meta:
        model = Job
        fields = [
            "location",
            "job_type",
            "is_active",
            "company_name",
            "category",
            "category_name",
            "company_display_name",
        ]
