from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import User

from .models import Staff


@receiver(post_save, sender=User)
def create_staff(sender, instance: User, created, **kwargs):
    if created and instance.is_staff:
        Staff.objects.create(user=instance)
