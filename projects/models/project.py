from django.db import models
from contracts.models import Contract
from projects.models.milestone import Milestone, Acknowledgement


class ProjectStatusChoices(models.TextChoices):
    CLOSED = "CLOSED"
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    TERMINATED = "TERMINATED"


class Project(models.Model):

    duration = models.CharField(max_length=255)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)

    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    milestones = models.ManyToManyField(
        Milestone, related_name="milestone_project", blank=True
    )
    acknowledgement = models.ForeignKey(
        Acknowledgement,
        on_delete=models.SET_NULL,
        related_name="project",
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=ProjectStatusChoices.choices,
        default=ProjectStatusChoices.PENDING,
    )

    acceptance_comment = models.TextField(max_length=1000, null=True, blank=True)
    completion_comment = models.TextField(max_length=1000, null=True, blank=True)
    termination_comment = models.TextField(max_length=1000, null=True, blank=True)
    cancellation_comment = models.TextField(max_length=1000, null=True, blank=True)

    system_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    @property
    def client(self):
        return self.contract.client

    @property
    def freelancer(self):
        return self.contract.freelancer

    @property
    def job(self):
        return self.contract.job
