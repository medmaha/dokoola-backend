from django.db import models
from projects.models.acknowledgement import Acknowledgement


class MilestoneStatusChoices(models.TextChoices):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ACCEPTED = "ACCEPTED"
    ACTIVE = "ACTIVE"


class Milestone(models.Model):
    project_pk = models.CharField(max_length=255, db_index=True)
    acknowledgement = models.ForeignKey(
        Acknowledgement, on_delete=models.SET_NULL, related_name="milestone", null=True
    )

    milestone_name = models.CharField(max_length=255, null=True, blank=True)
    milestone_description = models.TextField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_final = models.BooleanField(default=False)
    status = models.CharField(
        max_length=255,
        choices=MilestoneStatusChoices.choices,
        default=MilestoneStatusChoices.ACTIVE,
    )

    def get_project(self):
        project = self.project  # type: ignore
        return project
