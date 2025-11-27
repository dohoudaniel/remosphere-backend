from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from authentication.email_utils import send_welcome_email
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(post_save, sender=User)
def send_welcome_on_verification(sender, instance, created, **kwargs):
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
