from django.db import models
from freelancers.models import Freelancer
from .invitation import Invitation


class Activities(models.Model):
    bits_count = models.IntegerField(default=0)
    hired_count = models.IntegerField(default=0)
    invite_count = models.IntegerField(default=0)
    proposal_count = models.IntegerField(default=0)
    interview_count = models.IntegerField(default=0)
    unanswered_invites = models.IntegerField(default=0)
    hired = models.ManyToManyField(Freelancer, blank=True)
    client_last_visit = models.DateTimeField(null=True, blank=True)
    proposals = models.ManyToManyField("proposals.Proposal", related_name="proposals")
    invitations = models.ManyToManyField(Invitation, related_name="activity")
