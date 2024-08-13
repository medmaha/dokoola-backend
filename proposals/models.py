from django.db import models
from jobs.models import Job
from freelancers.models import Freelancer


class ProposalStatusChoices(models.TextChoices):
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    PENDING = "PENDING"


class Proposal(models.Model):

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="proposals")

    freelancer = models.ForeignKey(
        Freelancer, on_delete=models.CASCADE, related_name="proposals"
    )

    duration = models.CharField(max_length=100, null=True, blank=True)
    cover_letter = models.TextField(max_length=1500)
    attachments = models.ManyToManyField("Attachment", related_name="proposal")

    budget = models.FloatField(default=0, blank=True)
    service_fee = models.FloatField(default=0.00, blank=True, help_text="In percentage")
    bits_amount = models.IntegerField(default=12, blank=True)

    is_reviewed = models.BooleanField(default=False)

    status = models.CharField(
        max_length=200, choices=ProposalStatusChoices.choices, default="PENDING"
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Attachment(models.Model):
    name = models.CharField(max_length=100)
    file_url = models.CharField(max_length=1500)
