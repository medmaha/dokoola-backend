import random
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification

from proposals.models import Proposal


@receiver(post_save, sender=Proposal)
def notification_proposals(sender, instance: Proposal, created, **kwargs):
    """
    Listen to database dispatching event for the Proposal model
    - Check to see if a new job proposal (freelancer proposed to a job) is created
    - Then create a new notification for the job creator
    """

    def create_hint_text(freelancer):
        hints = [
            "You've received a new application",
            "A new proposal from your job posting",
            f"An Application from {freelancer.name}",
            f"{freelancer.name} has proposed for your job",
        ]

        hint = random.choice(hints)

        return hint

    if created:
        client = instance.job.client.user
        freelancer = instance.freelancer.user

        notification = Notification()
        notification.sender = freelancer
        notification.recipient = client
        notification.hint_text = create_hint_text(freelancer)
        notification.content_text = f"{instance.cover_letter[:125]}" + (
            "..." if len(instance.cover_letter) > 125 else ""
        )
        notification.object_api_link = f"/proposals/view/{instance.pk}"
        notification.type = "PROPOSAL"
        notification.save()
