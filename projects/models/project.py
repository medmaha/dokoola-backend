from django.db import models

from contracts.models import Contract
from projects.models.milestone import Acknowledgement, Milestone


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
    def talent(self):
        return self.contract.talent

    @property
    def job(self):
        return self.contract.job

    @classmethod
    def _active_statuses(cls):
        return [ProjectStatusChoices.ACCEPTED, ProjectStatusChoices.PENDING]

    def _terminate(self, reason=None, commit_save=True):
        self.status = ProjectStatusChoices.TERMINATED
        self.termination_comment = reason
        self.save()

    def milestones(self):
        from .milestone import Milestone

        _milestones = Milestone.objects.filter(project_pk=self.pk)
        return _milestones
