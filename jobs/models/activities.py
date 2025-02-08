from functools import partial
from django.db import models

from talents.models import Talent  # Updated import
from utilities.generator import primary_key_generator, public_id_generator, default_pid_generator

class Activities(models.Model):

    public_id = models.CharField(max_length=50, db_index=True, default=partial(default_pid_generator, "Activities"))
    
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


    def save(self, *args, **kwargs):
        if (self._state.adding):
            _id = primary_key_generator()
            self.public_id =public_id_generator(_id, "Activities")
        return super().save(*args, **kwargs)
