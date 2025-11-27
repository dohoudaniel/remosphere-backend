"""Signal handlers related to user lifecycle events.

The primary handler in this module fires a welcome-email Celery
task when a user's `email_verified` flag transitions from False to True.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from authentication.email_utils import send_welcome_email
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(post_save, sender=User)
def send_welcome_on_verification(sender, instance, created, **kwargs):
    """
    Send a welcome email asynchronously when a user verifies email.

    Only triggers when the saved instance is not newly created and the
    verification state changed from False to True.
    """
    # Trigger welcome when user toggles from unverified -> verified
    if not created:
        prev = getattr(instance, "_previous_is_verified", False)
        current = getattr(instance, "email_verified", False)

        logger.info(
            "signal: prev=%s, current=%s, created=%s, user=%s",
            prev,
            current,
            created,
            instance.email)

        if (not prev) and current:
            # send task with primitive args
            send_welcome_email.delay(instance.email, instance.first_name)
