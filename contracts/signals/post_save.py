from django.db.models.signals import post_save
from django.dispatch import receiver
from jobs.models import JobStatusChoices
from notifications.models import Notification
from contracts.models import Contract, ContractStatusChoices, ContractProgressChoices


@receiver(post_save, sender=Contract)
def on_accepted_contract(sender, instance: Contract, created, **kwargs):

    if not instance.status == ContractStatusChoices.ACCEPTED:
        return

    if not instance.progress == ContractProgressChoices.NONE:
        return

    instance.progress = ContractProgressChoices.ACTIVE
    instance.job.status = JobStatusChoices.IN_PROGRESS
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


@receiver(post_save, sender=Contract)
def on_completed_contract(sender, instance: Contract, created, **kwargs):

    if not instance.progress == ContractProgressChoices.COMPLETED:
        return

    client = instance.client
    freelancer = instance.freelancer

    # Notify the freelancer
    Notification.objects.create(
        hint_text="Project Completed",
        content_text=f"You've marked the contract {instance.pk}: {instance.job.title} as <strong>{instance.progress}</strong>! Dokoola congrats you for this 🎇",
        recipient=freelancer.user,
        object_api_link=f"/contracts/view/{instance.pk}",
    )
    # TODO: Notify freelancer through email
    # Notify the freelancer
    Notification.objects.create(
        hint_text="Project Awaiting Review",
        content_text=f"We'll prompt <strong>{instance.client.user.name}</strong> to review and validate your work",
        recipient=freelancer.user,
        object_api_link=f"/contracts/view/{instance.pk}",
    )
    # TODO: Notify freelancer through email

    # Notify the client
    Notification.objects.create(
        hint_text="Project Completed",
        content_text=f"Your contract {instance.pk}: {instance.job.title} was marked completed by <strong>{freelancer.user.name}</strong> please review and acknowledge the status",
        recipient=client.user,
        sender=freelancer.user,
        object_api_link=f"/contracts/view/{instance.pk}",
    )
    # TODO: Notify client through email
