from django.db import models
from talents.models import Talent  # Updated import


class Activities(models.Model):
    job = models.OneToOneField(
        "Job", on_delete=models.CASCADE, null=True, related_name="activity"
    )
    bits_count = models.IntegerField(default=0)
    hired_count = models.IntegerField(default=0)
    invite_count = models.IntegerField(default=0)
    proposal_count = models.IntegerField(default=0)
    interview_count = models.IntegerField(default=0)
    unanswered_invites = models.IntegerField(default=0)
    hired = models.ManyToManyField(Talent, blank=True)  # Updated from Talent to Talent
    client_last_visit = models.DateTimeField(null=True, blank=True)
