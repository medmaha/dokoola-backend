from django.db import models

from clients.models import Client
from proposals.models import Job, Proposal, Talent
from utilities.generator import primary_key_generator, public_id_generator


class ContractProgressChoices(models.TextChoices):
    NONE = "NONE"
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class ContractStatusChoices(models.TextChoices):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    TERMINATED = "TERMINATED"


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
    Contract model represents a contract between a client and a talent
    for a specific job.
    It holds the negotiation state, the terms of the contract, and the status of the contract.
    """

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    proposal = models.ForeignKey(
        Proposal, on_delete=models.CASCADE, related_name="contract"
    )
    talent = models.ForeignKey(Talent, on_delete=models.CASCADE)

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

    # Whether the client has acknowledged the work done by the talent
    talent_acknowledgement = models.CharField(
        max_length=200,
        choices=ContractStatusChoices.choices,
        default="PENDING",
    )

    client_comment = models.CharField(
        max_length=200, choices=ContractStatusChoices.choices, blank=True, null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    public_id = models.CharField(null=True, blank=True, db_index=True, max_length=50)

    PUBLIC_ID_PREFIX = "C"

    def __str__(self) -> str:
        return f"Contract: {self.job.title}"

    def save(self, *args, **kwargs):
        if not self.public_id:
            _id = self.pk or primary_key_generator()
            self.public_id = public_id_generator(_id, self.PUBLIC_ID_PREFIX)
        return super().save(*args, **kwargs)

    @classmethod
    def _active_statuses(cls):
        return [ContractStatusChoices.ACCEPTED, ContractStatusChoices.PENDING]

    def _terminate(self, reason=None, commit_save=True):
        self.status = ContractStatusChoices.TERMINATED
        self.client_comment = reason
        self.save()
