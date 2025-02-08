from functools import partial
from django.db import models

from jobs.models import  Job
from talents.models import Talent  # Updated import
from utilities.generator import primary_key_generator, public_id_generator, default_pid_generator


class ProposalStatusChoices(models.TextChoices):
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    PENDING = "PENDING"


class Proposal(models.Model):
    public_id = models.CharField(max_length=50, default=partial(default_pid_generator, "Proposal"))

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="proposals")

    talent = models.ForeignKey(  # Renamed from talent to talent
        Talent, on_delete=models.CASCADE, related_name="proposals"
    )

    duration = models.CharField(max_length=100, null=True, blank=True)
    cover_letter = models.TextField(max_length=1500)
    attachments = models.ManyToManyField("Attachment", related_name="proposal")

    budget = models.FloatField(default=0, blank=True)
    service_fee = models.FloatField(default=0.00, blank=True, help_text="In percentage")
    bits_amount = models.IntegerField(default=12, blank=True)

    is_reviewed = models.BooleanField(default=False)

    status = models.CharField(
        max_length=200,
        choices=ProposalStatusChoices.choices,
        default="PENDING",
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if (self._state.adding):
            _id = self.id or primary_key_generator()
            self.public_id = public_id_generator(_id, "Proposal")
        return super().save(*args, **kwargs)



class Attachment(models.Model):
    public_id = models.CharField(max_length=50, default=partial(default_pid_generator, "Attachment"))

    name = models.CharField(max_length=100)
    file_url = models.CharField(max_length=1500)


    def save(self, *args, **kwargs):
        if (self._state.adding):
            _id = self.id or primary_key_generator()
            self.public_id = public_id_generator(_id, "Attachment")
        return super().save(*args, **kwargs)
