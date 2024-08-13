from django.db import models
from clients.models import Client
from proposals.models import Proposal, Job, Freelancer


class ContractProgressChoices(models.TextChoices):
    NONE = "NONE"
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class ContractStatusChoices(models.TextChoices):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class NegotiationStatusChoices(models.TextChoices):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class Negotiation(models.Model):
    """
    Negotiation model represents the negotiation state of a contract.
    It holds the terms of the negotiation and the status of the negotiation.
    """

    terms = models.TextField(max_length=1500, null=True, blank=True)
    status = models.CharField(
        max_length=200,
        choices=NegotiationStatusChoices.choices,
        default=NegotiationStatusChoices.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Contract(models.Model):
    """
    Contract model represents a contract between a client and a freelancer
    for a specific job.
    It holds the negotiation state, the terms of the contract, and the status of the contract.
    """

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

    completed_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=200,
        choices=ContractStatusChoices.choices,
        default=ContractStatusChoices.PENDING,
    )

    progress = models.CharField(
        max_length=200,
        choices=ContractProgressChoices.choices,
        default=ContractProgressChoices.NONE,
    )

    deleted = models.BooleanField(default=False, blank=True)

    # negotiation = models.ManyToManyField(
    #     Negotiation, related_name="contract", blank=True
    # )

    # Whether the client has acknowledged the work done by the freelancer
    freelancer_acknowledgement = models.CharField(
        max_length=200, choices=ContractStatusChoices.choices, default="PENDING"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Contract: {self.job.title}"
