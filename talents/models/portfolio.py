from functools import partial

from django.db import models
from django.db.models.manager import Manager

from reviews.models import Review
from users.models import User
from utilities.generator import (
    default_pid_generator,
    primary_key_generator,
    public_id_generator,
)


class Portfolio(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    url = models.URLField()
    image = models.CharField(max_length=2000)

    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    public_id = models.CharField(max_length=50, db_index=True, blank=True)

    def save(self, *args, **kwargs):
        if self._state.adding or not self.public_id:
            _id = self.pk or primary_key_generator()
            self.public_id = public_id_generator(_id, "Portfolio")
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name
