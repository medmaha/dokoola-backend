from functools import partial
import random

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from clients.models import Client
from core.models import Category
from core.services.email.main import EmailService
from utilities.generator import (
    primary_key_generator,
    public_id_generator,
    default_pid_generator,
)


class JobStatusChoices(models.TextChoices):
    CLOSED = "CLOSED"
    PUBLISHED = "PUBLISHED"
    SUSPENDED = "SUSPENDED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

    @classmethod
    def verify_status(cls, status: str):
        if status not in cls.values:
            return False
        return True


class JobTypeChoices(models.TextChoices):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    FREELANCE = "freelance"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    OTHER = "other"


class Job(models.Model):
    id = models.UUIDField(
        primary_key=True, default=primary_key_generator, editable=False
    )
    public_id = models.CharField(
        max_length=50, db_index=True, default=partial(default_pid_generator, "Job")
    )

    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()

    pricing = models.JSONField(encoder=DjangoJSONEncoder, blank=True, null=True)
    benefits = models.JSONField(encoder=DjangoJSONEncoder, blank=True, null=True)
    required_skills = models.JSONField(encoder=DjangoJSONEncoder, blank=True, null=True)

    country = models.JSONField(encoder=DjangoJSONEncoder)
    address = models.CharField(max_length=200, blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    job_type = models.CharField(
        max_length=20,
        choices=JobTypeChoices.choices,
        default=JobTypeChoices.FREELANCE,
        db_index=True,
    )

    published = models.BooleanField(default=False, blank=True)
    status = models.CharField(
        max_length=200, choices=JobStatusChoices.choices, default="CLOSED"
    )

    is_valid = models.BooleanField(default=True, blank=True)
    is_third_party = models.BooleanField(default=False, blank=True)
    third_party_address = models.URLField(blank=True, null=True)

    views_count = models.IntegerField(default=0)
    proposal_count = models.IntegerField(default=0)
    invitation_count = models.IntegerField(default=0)
    client_last_visit = models.DateTimeField(blank=True, null=True)

    job_type_other = models.CharField(blank=True, null=True, max_length=200)
    experience_level_other = models.CharField(blank=True, null=True, max_length=200)

    estimated_duration = models.DateTimeField(blank=True, null=True)
    application_deadline = models.DateTimeField(blank=True, null=True)
    additional_payment_terms = models.CharField(blank=True, default="")
    experience_level = models.CharField(blank=True, null=True, max_length=200)

    client = models.ForeignKey(
        Client, related_name="jobs", on_delete=models.CASCADE, null=False
    )

    bits_amount = models.IntegerField(default=16)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title[:50]

    class Meta:
        ordering = ["is_valid", "-created_at", "published"]

    def save(self, *args, **kwargs):
        if self.third_party_address:
            self.is_third_party = True
        if self._state.adding:
            _id = self.id or primary_key_generator()
            self.public_id = public_id_generator(_id, "Job")

        return super().save(*args, **kwargs)

    def update_status_and_withdraw_proposals(
        self, job_status=None, is_after_response=True
    ):
        """
        Update the job status and notify the client and talent about the status through email
        """

        if JobStatusChoices.verify_status(job_status):
            self.status = job_status
            self.save()

        from proposals.models import Proposal, ProposalStatusChoices

        other_proposals = (
            Proposal.objects.select_related("talent__user")
            .filter(
                job=self,
                status__in=[
                    ProposalStatusChoices.REVIEW,
                    ProposalStatusChoices.PENDING,
                ],
            )
            .exclude(status=ProposalStatusChoices.ACCEPTED)
        )

        for other_proposal in other_proposals:
            other_proposal.status = ProposalStatusChoices.WITHDRAWN
            other_proposal.notify_talent(
                ProposalStatusChoices.WITHDRAWN, is_after_response=is_after_response
            )

        Proposal.objects.bulk_update(other_proposals, ["status"])

    def notify_client(
        self, job_status, proposal=None, new_proposal=None, is_after_response=True
    ):
        """
        Notify the client about the job status through email
        """

        sender_name = "Dokoola Team"
        html_template_context = {
            "job": self,
            "client": self.client,
        }

        if new_proposal:
            subjects = [
                "New Application",
                "New Proposal",
                "New Job Proposal",
                "New Job Application",
            ]
            subject = random.choice(subjects)
            sender_name = new_proposal.talent.name
            html_template_context["proposal"] = new_proposal
            html_template_name = "emails/jobs/new_proposal.html"

        elif job_status == JobStatusChoices.IN_PROGRESS:
            subject = "Job Proposal Accepted"
            html_template_context["proposal"] = proposal
            html_template_name = "emails/jobs/proposal_accepted_client.html"

        elif job_status == JobStatusChoices.COMPLETED:
            subject = "Job Completed"
            html_template_name = "emails/jobs/job_completed.html"

        elif job_status == JobStatusChoices.CLOSED:
            subject = "Job Closed"
            html_template_name = "emails/jobs/job_closed.html"

        elif job_status == JobStatusChoices.SUSPENDED:
            subject = "Job Suspended"
            html_template_name = "emails/jobs/job_suspended.html"

        elif job_status == JobStatusChoices.PUBLISHED:
            subject = "Job Published"
            html_template_name = "emails/jobs/job_published.html"

        else:
            return

        email_service = EmailService()
        email_service.send(
            self.client.user.email,
            subject,
            sender_name=sender_name,
            html_template_name=html_template_name,
            html_template_context=html_template_context,
            execute_now=is_after_response == True,
        )

    @property
    def activities(self):
        from .activities import Activities

        activities, _ = Activities.objects.get_or_create(job=self)

        return activities
