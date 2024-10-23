import random

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import strip_tags

from core.services.email.main import EmailService
from proposals.models import Proposal

from .models import Notification


@receiver(post_save, sender=Notification)
def send_email_notification(sender, instance: Notification, created, **kwargs):
    if created:
        subject = instance.hint_text
        email = instance.recipient.email
        text = strip_tags(instance.content_text or "")
        html_template_name = "core/default_email.html"

        html_template_context = {"content": text}

        EmailService().send(
            email,
            subject,
            text,
            html_template_name=html_template_name,
            html_template_context=html_template_context,
        )


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

    if created:
        client = instance.job.client.user
        talent = instance.talent.user

        notification = Notification()
        notification.sender = talent
        notification.recipient = client
        notification.hint_text = create_hint_text(talent)
        notification.content_text = f"{instance.cover_letter[:125]}" + (
            "..." if len(instance.cover_letter) > 125 else ""
        )
        notification.object_api_link = f"/proposals/view/{instance.pk}"
        notification.type = "PROPOSAL"
        notification.save()
