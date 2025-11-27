from django.conf import settings
from django.db import models
from django.utils.text import slugify

class Job(models.Model):
    JOB_TYPE_FULL_TIME = "full_time"
    JOB_TYPE_PART_TIME = "part_time"
    JOB_TYPE_CONTRACT = "contract"
    JOB_TYPE_INTERNSHIP = "internship"
    JOB_TYPE_OTHER = "other"

    JOB_TYPE_CHOICES = [
        (JOB_TYPE_FULL_TIME, "Full time"),
        (JOB_TYPE_PART_TIME, "Part time"),
        (JOB_TYPE_CONTRACT, "Contract"),
        (JOB_TYPE_INTERNSHIP, "Internship"),
        (JOB_TYPE_OTHER, "Other"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(
        "categories.Category",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="jobs",
        db_index=True
    )
    location = models.CharField(max_length=128, db_index=True)
    job_type = models.CharField(max_length=32, choices=JOB_TYPE_CHOICES)
    salary_range = models.CharField(max_length=64, null=True, blank=True)
    company_name = models.CharField(max_length=255)
    company = models.ForeignKey(
        "companies.Company",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="jobs",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="jobs_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    slug = models.URLField(max_length=255, unique=True, blank=True)

    # optional expiry that can flip is_active if you want
    expiry_at = models.DateTimeField(null=True, blank=True, help_text="Optional expiry date after which is_active may be set to False.")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["location"]),
            models.Index(fields=["category"]),
            models.Index(fields=["job_type"]),
        ]

    def __str__(self):
        return f"{self.title} @ {self.company_name}"
