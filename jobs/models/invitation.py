from functools import partial
from django.db import models

from talents.models import Talent
from utilities.generator import primary_key_generator, public_id_generator, default_pid_generator


class Invitation(models.Model):
    public_id = models.CharField(max_length=50, db_index=True, default=partial(default_pid_generator, "Invitation"))

    job_id = models.CharField(null=True, blank=True)
    talent = models.ForeignKey(Talent, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if (self._state.adding):
            _id = primary_key_generator()
            self.public_id = public_id_generator(_id, "Invitation")
        return super().save(*args, **kwargs)
