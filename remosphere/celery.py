import os
from celery import Celery

"""
The Celery functionality
responsible for the sending of emails.
"""

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "remosphere.settings")
app = Celery("remosphere")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
