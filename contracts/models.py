from django.db import models
from clients.models import Client
from proposals.models import Proposal, Job, Freelancer
from utilities.generator import hex_generator


class Contract(models.Model):
    class ContractStatusType(models.TextChoices):
        PENDING = "PENDING"
        ACCEPTED = "ACCEPTED"
        REJECTED = "REJECTED"

    class ContractProgressType(models.TextChoices):
        NONE = "NONE"
        ACTIVE = "ACTIVE"
        CANCELLED = "CANCELLED"
        COMPLETED = "COMPLETED"

    uid = models.CharField(default=hex_generator, editable=False, max_length=64)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    proposal = models.ForeignKey(
        Proposal, on_delete=models.CASCADE, related_name="contract"
    )
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    duration = models.CharField(max_length=100, null=True, blank=True)
    payment_method = models.CharField(max_length=100, null=True, blank=True)
    additional_terms = models.TextField(max_length=1500, null=True, blank=True)

    status = models.CharField(
        max_length=200, choices=ContractStatusType.choices, default="PENDING"
    )

    progress = models.CharField(
        max_length=200, choices=ContractProgressType.choices, default="NONE"
    )

    deleted = models.BooleanField(default=False, blank=True)

    client_acknowledgement = models.CharField(
        max_length=200, choices=ContractStatusType.choices, default="PENDING"
    )
    freelancer_acknowledgement = models.CharField(
        max_length=200, choices=ContractStatusType.choices, default="PENDING"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return "Contract: " + self.uid
