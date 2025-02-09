import random

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import strip_tags

from core.services.email.main import EmailService
from proposals.models import Proposal, ProposalStatusChoices

from .models import Notification


@receiver(post_save, sender=Notification)
def send_email_notification(sender, instance: Notification, created, **kwargs):
    """
    - Check to see if a new notification is created
    - If it is, and it is not already emailed, send an email to the recipient
    """
    if created and not instance.is_emailed:
        subject = instance.hint_text
        email = instance.recipient.email
        text = strip_tags(instance.content_text or "")
        html_template_name = "emails/default.html"
        html_template_context = {"content": text}

        EmailService().send(
            email,
            subject,
            text,
            html_template_name=html_template_name,
            html_template_context=html_template_context,
        )

        instance.is_emailed = True
        instance.save()


@receiver(post_save, sender=Proposal)
def notification_proposals(sender, instance: Proposal, created, **kwargs):
    """
    Listen to database dispatching event for the Proposal model
    - Check to see if a new job proposal (talent proposed to a job) is created
    - Then create a new notification for the job creator
    """

    def create_hint_text(talent):
        hints = [
            "You've received a new application",
            "A new proposal from your job posting",
            f"An Application from {talent.name}",
            f"{talent.name} has proposed for your job",
        ]

        hint = random.choice(hints)

        return hint

    talent = instance.talent.user
    client = instance.job.client.user

    if created:
        notification = Notification()
        notification.sender = talent
        notification.recipient = client
        notification.hint_text = create_hint_text(talent)
        notification.content_text = strip_tags(
            f"{instance.cover_letter[:125]}"
            + ("..." if len(instance.cover_letter) > 125 else "")
        )
        notification.object_api_link = f"/proposals/{instance.public_id}"
        notification.type = "PROPOSAL"
        notification.save()
        return

    if instance.status == ProposalStatusChoices.ACCEPTED:
        notification = Notification()
        notification.sender = client
        notification.recipient = talent
        notification.hint_text = "Your proposal has been accepted!"
        notification.content_text = f"Congratulations! {client.name} has accepted your proposal for the job '{instance.job.title}'. You can now proceed with discussing the project details and timeline."
        notification.object_api_link = f"/proposals/{instance.public_id}"
        notification.type = "PROPOSAL"
        notification.save()
        return

    if instance.status == ProposalStatusChoices.DECLINED:
        notification = Notification()
        notification.sender = client
        notification.recipient = talent
        notification.hint_text = "Your proposal has been declined"
        notification.content_text = f"{client.name} has declined your proposal for the job '{instance.job.title}'."
        notification.object_api_link = f"/proposals/{instance.public_id}"
        notification.type = "PROPOSAL"
        notification.save()
        return

    if instance.status == ProposalStatusChoices.WITHDRAWN:
        notification = Notification()
        notification.sender = client
        notification.recipient = talent
        notification.hint_text = "Proposal withdrawn"
        notification.content_text = f"Your proposal for the job '{instance.job.title}' has been withdrawn."
        notification.object_api_link = f"/proposals/{instance.public_id}"
        notification.type = "PROPOSAL"
        notification.save()
        return
    
    if instance.status == ProposalStatusChoices.TERMINATED:
        notification = Notification()
        notification.recipient = talent
        notification.hint_text = "Proposal terminated"
        notification.content_text = f"The proposal for the job '{instance.job.title}' has been terminated."
        notification.object_api_link = f"/proposals/{instance.public_id}"
        notification.type = "PROPOSAL"
        notification.save()
        return