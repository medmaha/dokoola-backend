from functools import partial

from django.db import models

from core.services.email.main import EmailService
from jobs.models import Job
from talents.models import Talent  # Updated import
from utilities.generator import (
    default_pid_generator,
    primary_key_generator,
    public_id_generator,
)


class ProposalStatusChoices(models.TextChoices):
    REVIEW = "REVIEW"
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    CONTRACTED = "CONTRACTED"
    DECLINED = "DECLINED"
    WITHDRAWN = "WITHDRAWN"
    TERMINATED = "TERMINATED"


class Proposal(models.Model):
    public_id = models.CharField(
        max_length=50, db_index=True, default=partial(default_pid_generator, "PR")
    )

    job = models.ForeignKey(
        Job, on_delete=models.CASCADE, db_index=True, related_name="proposals"
    )
    talent = models.ForeignKey(  # Renamed from talent to talent
        Talent, on_delete=models.CASCADE, db_index=True, related_name="proposals"
    )

    duration = models.CharField(max_length=100, null=True, blank=True)
    cover_letter = models.TextField(max_length=1500)
    attachments = models.ManyToManyField(
        "Attachment", related_name="proposal", blank=True
    )

    budget = models.FloatField(default=0, blank=True)
    service_fee = models.FloatField(default=0.00, blank=True, help_text="In percentage")
    bits_amount = models.IntegerField(default=12, blank=True)

    is_reviewed = models.BooleanField(default=False)
    client_comment = models.TextField(max_length=500, null=True, blank=True)

    status = models.CharField(
        max_length=200,
        choices=ProposalStatusChoices.choices,
        default="PENDING",
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def _active_statuses(cls):
        return [
            ProposalStatusChoices.REVIEW,
            ProposalStatusChoices.PENDING,
            ProposalStatusChoices.ACCEPTED,
        ]

    def _terminate(self, reason=None, commit_save=True):
        self.status = ProposalStatusChoices.TERMINATED
        self.client_comment = reason
        self.save()

    def notify_talent(self, status: ProposalStatusChoices, is_after_response=True):
        """
        Notify the talent about the proposal status
        """

        subject = ""
        sender_name = "Dokoola Team"
        html_template_name = ""
        html_template_context = {
            "job": self.job,
            "proposal": self,
            "talent": self.talent,
        }

        if status == ProposalStatusChoices.ACCEPTED:
            subject = "Job Proposal Accepted"
            sender_name = self.job.client.name
            html_template_name = "emails/jobs/proposal_accepted_talent.html"
        elif status == ProposalStatusChoices.DECLINED:
            subject = "Job Proposal Declined"
            sender_name = self.job.client.name
            html_template_name = "emails/jobs/proposal_declined.html"
        elif status == ProposalStatusChoices.WITHDRAWN:
            subject = "Job Proposal Withdrawn"
            html_template_name = "emails/jobs/proposal_withdrawn.html"

        email_service = EmailService()

        email_service.send(
            self.talent.user.email,
            subject,
            sender_name=sender_name,
            html_template_name=html_template_name,
            html_template_context=html_template_context,
            execute_now=is_after_response == True,
        )

    def save(self, *args, **kwargs):
        if self._state.adding:
            _id = self.pk or primary_key_generator()
            self.public_id = public_id_generator(_id, "PR")
        elif self.status == ProposalStatusChoices.REVIEW and self.is_reviewed == False:
            self.is_reviewed = True
        return super().save(*args, **kwargs)


class Attachment(models.Model):
    public_id = models.CharField(
        max_length=50,
        db_index=True,
        default=partial(default_pid_generator, "A"),
    )

    name = models.CharField(max_length=100)
    file_url = models.CharField(max_length=1500)

    def save(self, *args, **kwargs):
        if self._state.adding:
            _id = primary_key_generator()
            self.public_id = public_id_generator(_id, "A")
        return super().save(*args, **kwargs)
