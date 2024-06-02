from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.text import slugify

from utilities.generator import hex_generator
from .models import Activities, Job


@receiver(pre_save, sender=Job)
def create_activities(sender, instance: Job, **kwargs):
    if not instance.slug:
        instance.slug = slugify(f"j-{hex_generator(14)}")


@receiver(pre_save, sender=Activities)
def update_activities(sender, instance: Activities, **kwargs):
    if instance.pk:
        instance.hired_count = instance.hired.count()
        instance.invite_count = instance.invitations.count()
        instance.proposal_count = instance.proposals.count()
