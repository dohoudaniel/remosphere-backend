from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
    """
    Category/Industry for jobs (e.g., Engineering, Product, Design).
    - 'name' is unique and human-readable.
    - 'slug' is generated from name and kept unique.
    - 'created_at' records when the category was added.
    """

    name = models.CharField(max_length=150, unique=True, db_index=True)
    # slug = models.SlugField(max_length=160, unique=True, blank=True)
    description = models.TextField(
        blank=True, help_text="Optional description of this category.")
    created_at = models.DateTimeField(default=timezone.now, editable=False)
