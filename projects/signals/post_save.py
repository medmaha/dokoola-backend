from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.models import Notification
from contracts.models import Contract, ContractStatusChoices, ContractProgressChoices


@receiver(post_save, sender=Contract)
def on_accepted_contract(sender, instance: Contract, created, **kwargs):
    """Create a new Project when a contract is being accepted."""

    if not instance.status == ContractStatusChoices.ACCEPTED:
        return

    if not instance.progress == ContractProgressChoices.NONE:
        return

    # Update the contract progress
    instance.progress = ContractProgressChoices.ACTIVE
    # Update the job status
    instance.job.save()
    instance.save()

    client = instance.client
    freelancer = instance.freelancer

    # When an error occurred in the above transaction
    if not instance.progress == ContractProgressChoices.ACTIVE:
        return

    # Notify the freelancer
    Notification.objects.create(
        hint_text="Project Started",
        content_text=f"Your contract <strong>{instance.job.title}</strong> from <strong>{client.user.name}</strong> is due an active",
        recipient=freelancer.user,
        object_api_link=f"/contracts/view/{instance.pk}",
    )
    # TODO: Notify freelancer through email

    # Notify the client
    Notification.objects.create(
        hint_text="Project Started",
        content_text=f"Your contract <strong>{instance.job.title}</strong> with <strong>{freelancer.user.name}</strong> has commenced",
        recipient=client.user,
        object_api_link=f"/contracts/view/{instance.pk}",
    )
    # TODO: Notify client through email
