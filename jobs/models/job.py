import random
from functools import partial
from typing import List

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from agent.scrapper.base import ScrapedJob
from clients.models import Client
from core.models import Category
from core.services.email.main import EmailService
from utilities.generator import (
    default_pid_generator,
    primary_key_generator,
    public_id_generator,
)


class JobStatusChoices(models.TextChoices):
    CLOSED = "CLOSED"
    PUBLISHED = "PUBLISHED"
    SUSPENDED = "SUSPENDED"
    COMPLETED = "COMPLETED"
    IN_PROGRESS = "IN_PROGRESS"
    DELETED = "DELETED"

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
        primary_key=True, default=primary_key_generator, editable=False  # type: ignore
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
    job_type_other = models.CharField(blank=True, null=True, max_length=200)

    published = models.BooleanField(default=False, blank=True)
    status = models.CharField(
        max_length=200, choices=JobStatusChoices.choices, default="CLOSED"
    )

    is_valid = models.BooleanField(default=True, blank=True)
    is_deleted = models.BooleanField(default=True, blank=True)
    is_third_party = models.BooleanField(default=False, blank=True)
    third_party_address = models.URLField(blank=True, null=True)
    third_party_metadata = models.JSONField(
        encoder=DjangoJSONEncoder, blank=True, null=True
    )

    views_count = models.IntegerField(default=0)
    proposal_count = models.IntegerField(default=0)
    invitation_count = models.IntegerField(default=0)
    client_last_visit = models.DateTimeField(blank=True, null=True)

    experience_level = models.CharField(blank=True, null=True, max_length=200)
    experience_level_other = models.CharField(blank=True, null=True, max_length=200)

    estimated_duration = models.CharField(blank=True, null=True)
    application_deadline = models.DateTimeField(blank=True, null=True)
    additional_payment_terms = models.CharField(blank=True, default="")

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


class JobAgentProxy(Job):
    class Meta:
        proxy = True

    def save_scraped_jobs(self, _jobs: dict | List[ScrapedJob]) -> None:

        if len(_jobs) < 1:
            return

        if len(_jobs) == 0:
            return

        client = Client.objects.filter(is_agent=True).first()
        category = Category.objects.filter(is_agent=True).first()

        if not client or not category:
            return

        # Remove existing jobs
        existing_jobs = set(
            Job.objects.only("third_party_address")
            .filter(third_party_address__in=[job.url for job in _jobs])
            .values_list("third_party_address", flat=True)
        )

        _jobs = [job for job in _jobs if job.url not in existing_jobs]

        _lazy_jobs = []

        for job in _jobs:
            _lazy = Job(
                published=True,
                client=client,
                title=job.title,
                category=category,
                pricing=job.pricing,
                address=job.address,
                country=job.country,
                is_third_party=True,
                benefits=job.benefits,
                job_type=job.job_type,
                created_at=job.created_at,
                description=job.description,
                third_party_address=job.url,
                job_type_other=job.job_type_other,
                status=JobStatusChoices.PUBLISHED,
                required_skills=job.required_skills,
                application_deadline=job.application_deadline,
                third_party_metadata=job.third_party_metadata,
            )

            try:
                _lazy.full_clean()
            except Exception as e:
                # TODO: log error
                print(f"Error cleaning job {job.url}: {e}")
            _lazy_jobs.append(_lazy)

        Job.objects.bulk_create(_lazy_jobs)
