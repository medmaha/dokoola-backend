from django.db import models
from utilities.generator import hex_generator
from jobs.models import Job
from freelancers.models import Freelancer


class Proposal(models.Model):

    class ProposalStatusType(models.TextChoices):
        ACCEPTED = "ACCEPTED"
        DECLINED = "DECLINED"
        PENDING = "PENDING"

    uid = models.CharField(default=hex_generator, editable=False, max_length=64)

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="proposals")

    freelancer = models.ForeignKey(
        Freelancer, on_delete=models.CASCADE, related_name="proposals"
    )

    duration = models.CharField(max_length=100, null=True, blank=True)
    cover_letter = models.TextField(max_length=1500)
    attachments = models.ManyToManyField("Attachment", related_name="proposal")

    budget = models.FloatField(default=0, blank=True)
    service_fee = models.FloatField(default=0.06, blank=True, help_text="In percentage")
    bits_amount = models.IntegerField(default=12, blank=True)

    is_decline = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    is_reviewed = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=True)

    status = models.CharField(
        max_length=200, choices=ProposalStatusType.choices, default="PENDING"
    )

    deleted = models.BooleanField(default=False, blank=True)

    is_proposed = models.BooleanField(default=False)  # Might not be used

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Attachment(models.Model):
    name = models.CharField(max_length=100)
    file_url = models.CharField(max_length=1500)
