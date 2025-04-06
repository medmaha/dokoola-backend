import random

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from django.utils import timezone

from clients.models import Client
from core.models import Category
from core.services.email.main import EmailService
from utilities.generator import (
    primary_key_generator,
    public_id_generator,
)


class JobStatusChoices(models.TextChoices):
    CLOSED = "CLOSED"
    PENDING = "PENDING"
    PUBLISHED = "PUBLISHED"
    SUSPENDED = "SUSPENDED"
    COMPLETED = "COMPLETED"
    IN_PROGRESS = "IN_PROGRESS"
    DELETED = "DELETED"
    CONTRACTED = "CONTRACTED"

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


class JobManager(models.manager.BaseManager):

    def valid_only(self):
        return super().filter(is_valid=True)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs).distinct()

class Job(models.Model):
    id = models.UUIDField(
        primary_key=True, default=primary_key_generator, editable=False  # type: ignore
    )
    public_id = models.CharField(max_length=50, db_index=True, blank=True)

    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()

    pricing = models.JSONField(
        encoder=DjangoJSONEncoder, blank=True, null=True, default=dict
    )
    benefits = models.JSONField(
        encoder=DjangoJSONEncoder, blank=True, null=True, default=dict
    )
    required_skills = models.JSONField(
        encoder=DjangoJSONEncoder, blank=True, null=True, default=dict
    )

    country = models.JSONField(encoder=DjangoJSONEncoder)
    address = models.CharField(max_length=200, blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    job_type = models.CharField(
        max_length=20,
        choices=JobTypeChoices.choices,
        default=JobTypeChoices.FREELANCE,
        db_index=True,
    )
    job_type_other = models.CharField(blank=True, null=True, max_length=200)

    published = models.BooleanField(default=False, blank=True)
    status = models.CharField(
        max_length=200,
        choices=JobStatusChoices.choices,
        default=JobStatusChoices.PENDING,
    )

    is_valid = models.BooleanField(default=True, blank=True)
    is_deleted = models.BooleanField(default=True, blank=True)
    is_third_party = models.BooleanField(default=False, blank=True)
    third_party_address = models.URLField(blank=True, null=True)
    third_party_metadata = models.JSONField(
        encoder=DjangoJSONEncoder, blank=True, null=True
    )

    client_last_visit = models.DateTimeField(blank=True, null=True)
    metadata = models.JSONField(encoder=DjangoJSONEncoder, blank=True, default=dict, null=True)

    experience_level = models.CharField(blank=True, null=True, max_length=200)
    experience_level_other = models.CharField(blank=True, null=True, max_length=200)

    application_deadline = models.DateTimeField(blank=True, null=True)
    estimated_duration = models.CharField(blank=True, null=True, max_length=255)
    additional_payment_terms = models.CharField(blank=True, default="", max_length=255, null=True)

    client = models.ForeignKey(
        Client, related_name="jobs", on_delete=models.CASCADE, null=False
    )

    bits_amount = models.IntegerField(default=16, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    PUBLIC_ID_PREFIX = "Job"

    def __str__(self):
        return self.title[:50]

    def __title__(self):
        return self.title[:20]

    class Meta:
        ordering = ["is_valid", "-created_at", "published"]

    def budget(self):
        if not self.pricing or not not self.pricing.get("budget", None):
            return "N/A"

        currency = self.pricing.get("currency", "USD")
        return f"{currency} {self.pricing.get('budget')}"

    def deadline(self):
        return self.application_deadline

    def save(self, *args, **kwargs):
        if self.third_party_address:
            self.is_third_party = True
        if self._state.adding or not self.public_id:
            _id = self.pk or primary_key_generator()
            self.public_id = public_id_generator(_id, self.PUBLIC_ID_PREFIX)
        return super().save(*args, **kwargs)

    def update_status_and_withdraw_proposals(
        self, job_status=None, is_after_response=True
    ):
        """
        Update the job status and notify the client and talent about the withdrawal-status through email
        """

        if JobStatusChoices.verify_status(job_status or ""):
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


    def notify_client(self, job_status, proposal=None, new_proposal=None):
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
        )

    @property
    def activities(self):
        from .activities import Activities

        activities, _ = Activities.objects.get_or_create(job=self, defaults={
            "applicants_id": [],
        })

        return activities
