from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from django.contrib.auth import get_user_model
from authentication.email_utils import send_welcome_email

User = get_user_model()

@receiver(post_save, sender=User)
def send_welcome_on_verification(sender, instance, created, **kwargs):
    # Only fire when user switches from unverified to verified
    if not created and instance.is_verified and not instance._previous_is_verified:
        send_welcome_email(instance)

