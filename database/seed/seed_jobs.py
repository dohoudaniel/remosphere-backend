import json
import os
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings

from jobs.models import Job
from companies.models import Company
from categories.models import Category
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the Jobs table with initial data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="jobs.json",
            help="JSON file inside database/seed/",
        )

    def handle(self, *args, **options):
        file_name = options["file"]
        seed_file_path = os.path.join(
            settings.BASE_DIR, "database", "seed", file_name
        )

        if not os.path.exists(seed_file_path):
            self.stdout.write(self.style.ERROR(f"Seed file not found: {seed_file_path}"))
            return

        # Load the JSON file
        with open(seed_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        created_count = 0

        for item in data:
            # Handle category (nullable)
            category_obj = None
            if "category" in item and item["category"]:
                category_obj, _ = Category.objects.get_or_create(
                    name=item["category"]
                )

            # Handle company (nullable)
            company_obj = None
            if "company" in item and item["company"]:
                company_obj, _ = Company.objects.get_or_create(
                    name=item["company"]
                )

            # Handle created_by user (nullable)
            created_by_obj = None
            if "created_by_email" in item and item["created_by_email"]:
                created_by_obj = User.objects.filter(
                    email=item["created_by_email"]
                ).first()

            # Generate slug from title + company
            base_slug = slugify(f"{item['title']}-{item.get('company_name', '')}")
            slug = base_slug
            counter = 1
            while Job.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            # Create Job object
            job, created = Job.objects.get_or_create(
                title=item["title"],
                company_name=item["company_name"],
                defaults={
                    "description": item["description"],
                    "location": item["location"],
                    "job_type": item["job_type"],
                    "salary_range": item.get("salary_range", None),
                    "category": category_obj,
                    "company": company_obj,
                    "created_by": created_by_obj,
                    "expiry_at": item.get("expiry_at", None),
                    "slug": slug,
                    "is_active": item.get("is_active", True),
                },
            )

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"✓ Successfully seeded {created_count} Job entries.")
        )
