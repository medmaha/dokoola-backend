from django.db import models

from django.db import models
from freelancers.models import Freelancer


class Invitation(models.Model):
    interview_count = models.IntegerField(default=0)
    client_last_visit = models.DateTimeField(null=True, blank=True)
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE)
    proposals = models.ManyToManyField(
        "proposals.Proposal", related_name="job_proposals"
    )
    proposal = models.ForeignKey(
        "proposals.Proposal", on_delete=models.CASCADE, null=True
    )
    job = models.ForeignKey("Job", on_delete=models.CASCADE, related_name="invitations")
