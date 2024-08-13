from django.db.models.signals import pre_save
from django.dispatch import receiver
from jobs.models import Activities


@receiver(pre_save, sender=Activities)
def update_activities(sender, instance: Activities, **kwargs):
    """Updates counts in Activities model"""
    if instance.pk:
        instance.hired_count = instance.hired.count()
        instance.invite_count = instance.invitations.count()
        instance.proposal_count = instance.proposals.count()
