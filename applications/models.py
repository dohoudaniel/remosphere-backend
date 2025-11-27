from django.db import models
from django.conf import settings
from django.utils import timezone


class Application(models.Model):
    STATUS_APPLIED = "applied"
    STATUS_SHORTLISTED = "shortlisted"
    STATUS_REJECTED = "rejected"
    STATUS_WITHDRAWN = "withdrawn"
    STATUS_PENDING = "pending"

    STATUS_CHOICES = [
        (STATUS_APPLIED, "Applied"),
        (STATUS_SHORTLISTED, "Shortlisted"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_WITHDRAWN, "Withdrawn"),
        (STATUS_PENDING, "Pending"),
    ]

    job = models.ForeignKey(
        "jobs.Job",
        on_delete=models.CASCADE,
        related_name="applications",   # <--- important for job annotations
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    resume_url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_PENDING)
    applied_at = models.DateTimeField(default=timezone.now)

    class Meta:
        # ordering = ["-applied_at"]
        # Prevent duplicate applications by the same user to the same job
        # constraints = [
        #     models.UniqueConstraint(fields=["job", "user"], name="unique_job_user_application")
        # ]
        unique_together = ("job", "user")  # prevents duplicate applications

    def __str__(self):
        return f"{self.user_id} -> {self.job_id} ({self.status})"
