from django.db.models.signals import post_save
from django.dispatch import receiver

from jobs.models.activities import Activities
from jobs.models.job import Job, JobStatusChoices
from talents.models.talent import Talent

from ..models import Proposal

@receiver(post_save, sender=Proposal)
def update_job_details(sender, instance: Proposal, created, **kwargs):
    # Update the job's activity

    if created:
        activity, _ = Activities.objects.get_or_create(job=instance.job)
        _applicants_id: list =  activity.applicants_id or [] 
        applicants_id = set(_applicants_id) 
        applicants_id.add(instance.talent.public_id)
        activity.applicants_id = list(_applicants_id) # type: ignore
        activity.proposal_count = activity.proposal_count + 1
        activity.save()

        # Update the job's metadata
        metdata_data = instance.job.metadata or dict()
        metdata_data["has_proposal"] = True

        Job.objects.filter(id=instance.job.pk).update(metadata=metdata_data)

        # Update the talent's details
        talent_applicants_id = set(instance.talent.applications_ids or [])
        talent_applicants_id.add(instance.job.public_id)

        if not instance.job.is_third_party:
            bits = instance.talent.bits - instance.bits_amount
            Talent.objects.filter(id=instance.talent.pk).update(bits=bits, applications_ids=talent_applicants_id)
        else:
            Talent.objects.filter(id=instance.talent.pk).update(applications_ids=list(talent_applicants_id))

        # Notify the client
        instance.job.notify_client(
            JobStatusChoices.PUBLISHED, new_proposal=instance
        )