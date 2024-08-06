from django.db import models
from contracts.models import Contract
from projects.models.milestone import Milestone, Acknowledgement


class ProjectStatusChoices(models.TextChoices):
    PENDING = "pending"
    CLOSED = "closed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    TERMINATED = "terminated"


class Project(models.Model):
    deadline = models.DateTimeField()
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    milestones = models.ManyToManyField(Milestone, related_name="milestone_project")
    acknowledgement = models.ForeignKey(Acknowledgement, on_delete=models.SET_NULL, related_name="ack_project", null=True)

    status = models.CharField(max_length=20, choices=ProjectStatusChoices.choices, default=ProjectStatusChoices.PENDING)

    @property
    def client(self):
        return self.contract.client

    @property
    def freelancer(self):
        return self.contract.freelancer
    
    @property
    def job(self):
        return self.contract.job
