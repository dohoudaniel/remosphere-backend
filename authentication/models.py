from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(pre_save, sender=User)
def track_verification_before_save(sender, instance, **kwargs):
    if instance.pk:
        old = User.objects.filter(pk=instance.pk).first()
        instance._previous_is_verified = old.email_verified if old else False
    else:
        instance._previous_is_verified = False
