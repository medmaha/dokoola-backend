from django.db.models.signals import post_save
from django.dispatch import receiver
from projects.models import Project, ProjectStatusChoices

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
    talent = instance.talent

    # When an error occurred in the above transaction
    if not instance.progress == ContractProgressChoices.ACTIVE:
        return

    # Notify the talent
    Notification.objects.create(
        hint_text="Project Started",
        content_text=f"Your contract <strong>{instance.job.title}</strong> from <strong>{client.user.name}</strong> is due an active",
        recipient=talent.user,
        object_api_link=f"/contracts/view/{instance.pk}",
    )
    # TODO: Notify talent through email

    # Notify the client
    Notification.objects.create(
        hint_text="Project Started",
        content_text=f"Your contract <strong>{instance.job.title}</strong> with <strong>{talent.user.name}</strong> has commenced",
        recipient=client.user,
        object_api_link=f"/contracts/view/{instance.pk}",
    )
    # TODO: Notify client through email


@receiver(post_save, sender=Project)
def on_project_status_changed(sender, instance: Project, created, **kwargs):
    """Create a new Project when a contract is being accepted."""

    if instance.status == ProjectStatusChoices.PENDING:
        return

    client = instance.contract.client
    talent = instance.contract.talent

    if instance.status == ProjectStatusChoices.COMPLETED:
        # Notify the talent
        Notification.objects.create(
            hint_text="Project Completed",
            content_text=f"You've marked project <strong>{instance.contract.job.title}</strong> as COMPLETED we'll notify the client about this progress",
            recipient=talent.user,
            object_api_link=f"/projects/view/{instance.pk}",
        )
        # TODO: Notify talent through email

        # Notify the client
        Notification.objects.create(
            hint_text="Project Completed",
            content_text=f"You've a project awaiting your review, talent <strong>{talent.name}</strong> marked your project (<strong>{instance.contract.job.title}</strong>) as COMPLETED",
            recipient=client.user,
            object_api_link=f"/projects/view/{instance.pk}",
        )

    if instance.status == ProjectStatusChoices.CANCELLED:
        # Notify the talent
        Notification.objects.create(
            hint_text="Project Cancelled",
            content_text=f"You've Cancelled an going project (<strong>{instance.contract.job.title}</strong>). we don't know why but we respect your decision",
            recipient=talent.user,
            object_api_link=f"/projects/view/{instance.pk}",
        )

        # Notify the client
        Notification.objects.create(
            hint_text="Project Cancelled by Talent",
            content_text=f"Your ongoing project (<strong>{instance.contract.job.title}</strong>) was cancelled by talent <strong>{talent.name}</strong>. Reach out to the talent if there was a misunderstanding.",
            recipient=client.user,
            object_api_link=f"/projects/view/{instance.pk}",
        )

    if instance.status == ProjectStatusChoices.TERMINATED:

        # Notify the talent
        Notification.objects.create(
            hint_text="Project Terminated by Client",
            content_text=f"Your ongoing project (<strong>{instance.contract.job.title}</strong>) was terminated by client <strong>{client.name}</strong>. Reach out to the client if there was a misunderstanding.",
            recipient=talent.user,
            object_api_link=f"/projects/view/{instance.pk}",
        )

        # Notify the client
        Notification.objects.create(
            hint_text="Project Terminated",
            content_text=f"You've Terminated an going project (<strong>{instance.contract.job.title}</strong>). we don't know why but we respect your decision",
            recipient=client.user,
            object_api_link=f"/projects/view/{instance.pk}",
        )

    if instance.status == ProjectStatusChoices.ACCEPTED:

        # Notify the talent
        Notification.objects.create(
            hint_text="Project Accepted",
            content_text=f"Congratulations for service! Your completed project (<strong>{instance.contract.job.title}</strong>) was reviewed and accepted by client <strong>{client.name}</strong>.",
            recipient=talent.user,
            object_api_link=f"/projects/view/{instance.pk}",
        )

        # Notify the client
        Notification.objects.create(
            hint_text="Project Accepted",
            content_text=f"You've Accepted a submitted project (<strong>{instance.contract.job.title}</strong>) from <strong>{talent.name}</strong>, this actions means a lot for Dokoola",
            recipient=client.user,
            object_api_link=f"/projects/view/{instance.pk}",
        )

    # TODO: Notify users through email
