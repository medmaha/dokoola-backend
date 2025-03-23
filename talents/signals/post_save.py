from django.db.models.signals import post_save
from django.dispatch import receiver

from talents.models import Talent


@receiver(post_save, sender=Talent)
def create_talent(sender, instance: Talent, created, **kwargs):
    if created:
        user = instance.user
        if not user.is_talent:
            user.is_talent = True
            user.save()
