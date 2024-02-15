
from django.db.models.signals import post_save
from django.dispatch import receiver

from freelancers.models import Freelancer
            
@receiver(post_save, sender=Freelancer)
def create_freelancer(sender, instance:Freelancer, created, **kwargs):
    if created:
        user = instance.user
        if not user.is_freelancer:
            user.is_freelancer = True
            user.save()
