from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Client


@receiver(post_save, sender=Client)
def create_client(sender, instance: Client, created, **kwargs):
    if created:
        user = instance.user

        # Force the user of this profile to be a client
        if not user.is_client:
            user.is_client = True
            user.save()
