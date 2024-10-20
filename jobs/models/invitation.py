from django.db import models

from django.db import models
from talents.models import Talent


class Invitation(models.Model):
    job_id = models.CharField(null=True, blank=True)
    talent = models.ForeignKey(Talent, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
