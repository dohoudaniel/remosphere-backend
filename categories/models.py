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
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    description = models.TextField(blank=True, help_text="Optional description of this category.")
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ("name",)
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name

    def _generate_unique_slug(self):
        """
        Create a unique slug based on the name.
        If slug already exists, append a suffix like "-2", "-3", etc.
        """
        base_slug = slugify(self.name)[:140]  # keep some room for suffix
        slug = base_slug
        suffix = 1

        # If this instance already has a PK we should exclude it from the uniqueness check
        qs = Category.objects.all()
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        while qs.filter(slug=slug).exists():
            suffix += 1
            slug = f"{base_slug}-{suffix}"

        return slug

    def save(self, *args, **kwargs):
        # Ensure slug exists and is unique before saving.
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)
