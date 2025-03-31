from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from contracts.models import Contract, ContractProgressChoices, ContractStatusChoices
from jobs.models import JobStatusChoices
from notifications.models import Notification
from projects.models.project import Project


@receiver(post_save, sender=Contract)
def on_accepted_contract(sender, instance: Contract, created, **kwargs):
    """Fires when a contract is accepted.
    Specifically, when the contract is acknowledged by the talent.
    """

    # Return if the contract is not accepted
    if instance.status != ContractStatusChoices.ACCEPTED:
        return

    # Return if the contract is already active
    if instance.progress != ContractProgressChoices.NONE:
        return

    # Update the contract progress
    instance.progress = ContractProgressChoices.ACTIVE
    instance.save()

    # Update the job status
    instance.job.status = JobStatusChoices.IN_PROGRESS
    instance.job.save()

    client = instance.client
    talent = instance.talent

    project = Project()
    project.contract = instance
    project.duration = instance.duration or ""
    project.save()

    notifications = []

    # Congrats the talent
    notifications.append(
        Notification(
            hint_text="New Project 🎇",
            content_text=f"Congratulations on your new project <strong>{instance.job.title}</strong> from <strong>{client.user.name}</strong>",
            recipient=talent.user,
            object_api_link=f"/projects/view/{project.pk}",
        )
        # TODO: Notify talent through email
    )

    # Notify the talent
    notifications.append(
        Notification(
            hint_text="Project Timeline",
            content_text=f"Your new project <strong>{instance.job.title}</strong> from <strong>{client.user.name}</strong> is due on <strong>{instance.start_date.__format__('%Y-%m-%d %H:%M:%S')}</strong>",
            recipient=talent.user,
            object_api_link=f"/projects/view/{project.pk}",
        )
        # TODO: Notify talent through email
    )

    # Notify the client
    notifications.append(
        Notification(
            hint_text="Project Initiated",
            content_text=f"You've created a new project <strong>{instance.job.title}</strong> with <strong>{talent.user.name}</strong>",
            recipient=client.user,
            object_api_link=f"/projects/view/{project.pk}",
        )
        # TODO: Notify client through email
    )

    Notification.objects.bulk_create(notifications)


@receiver(post_save, sender=Contract)
def on_completed_contract(sender, instance: Contract, created, **kwargs):

    if instance.progress != ContractProgressChoices.COMPLETED:
        return

    if instance.completed_at is not None:
        return

    client = instance.client
    talent = instance.talent

    # Notify the talent
    Notification.objects.create(
        hint_text="Project Completed",
        content_text=f"You've marked the contract {instance.pk}: {instance.job.title} as <strong>{instance.progress}</strong>! Dokoola congrats you for this 🎇",
        recipient=talent.user,
        object_api_link=f"/contracts/view/{instance.pk}",
    )
    # TODO: Notify talent through email
    # Notify the talent
    Notification.objects.create(
        hint_text="Project Awaiting Review",
        content_text=f"We'll prompt <strong>{instance.client.user.name}</strong> to review and validate your work",
        recipient=talent.user,
        object_api_link=f"/contracts/view/{instance.pk}",
    )
    # TODO: Notify talent through email

    # Notify the client
    Notification.objects.create(
        hint_text="Project Completed",
        content_text=f"Your contract {instance.pk}: {instance.job.title} was marked completed by <strong>{talent.user.name}</strong> please review and acknowledge the status",
        recipient=client.user,
        sender=talent.user,
        object_api_link=f"/contracts/view/{instance.pk}",
    )

    instance.completed_at = timezone.now()
    instance.save()
    # TODO: Notify client through email
