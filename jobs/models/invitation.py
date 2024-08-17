from django.db import models

from django.db import models
from freelancers.models import Freelancer


class Invitation(models.Model):
    job_id = models.CharField(null=True, blank=True)
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
