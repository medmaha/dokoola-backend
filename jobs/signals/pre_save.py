from django.db.models.signals import pre_save
from django.dispatch import receiver
from jobs.models import Activities, Invitation
from proposals.models import Proposal


@receiver(pre_save, sender=Activities)
def update_activities(sender, instance: Activities, **kwargs):
    """Updates counts in Activities model"""
    if instance.pk:
        instance.hired_count = instance.hired.count()
        instance.invite_count = (
            Invitation.objects.select_related().filter(job_id=instance.pk).count()
        )
        instance.proposal_count = (
            Proposal.objects.select_related().filter(job__id=instance.pk).count()
        )
