from django.db import models
from datetime import datetime
from jobs.models import Job
from freelancers.models import Freelancer
from utilities.generator import hex_generator


class Proposal(models.Model):
    id = models.CharField(
        primary_key=True, default=hex_generator, editable=False, max_length=64
    )

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
    is_proposed = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def status(self):
        if self.is_accepted:
            return "ACCEPTED".capitalize()
        if self.is_decline:
            return "DECLINE".capitalize()
        return "PENDING".capitalize()


class Attachment(models.Model):
    name = models.CharField(max_length=100)
    file_url = models.CharField(max_length=1500)
