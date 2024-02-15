from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Staff
from users.models import User

@receiver(post_save, sender=User)
def create_staff(sender, instance:User, created, **kwargs):
    if created:
        if instance.is_staff:
            
            Staff.objects.create(user=instance)
        