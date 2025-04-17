from django.db import models

from talents.models import Talent
from utilities.generator import primary_key_generator, public_id_generator


class Activities(models.Model):

    public_id = models.CharField(
        max_length=50,
        db_index=True,
    )

    job = models.OneToOneField("Job", on_delete=models.CASCADE, related_name="activity")

    bits_count = models.IntegerField(db_default=0, default=0)
    hired_count = models.IntegerField(db_default=0, default=0)
    invite_count = models.IntegerField(db_default=0, default=0)
    proposal_count = models.IntegerField(db_default=0, default=0)
    interview_count = models.IntegerField(db_default=0, default=0)
    unanswered_invites = models.IntegerField(db_default=0, default=0)
    hired = models.ManyToManyField(Talent, blank=True)
    client_last_visit = models.DateTimeField(null=True, blank=True)

    applicants_id = models.JSONField(default=list, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self._state.adding or not self.public_id:
            _id = primary_key_generator()
            self.public_id = public_id_generator(_id, "Activities")
        return super().save(*args, **kwargs)

    def __job__(self):
        title = self.job.title

        if len(title) > 25:
            return title[:25] + "..."

        return title[:25]
