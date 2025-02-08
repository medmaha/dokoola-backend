from django.db import models
from functools import partial

from users.models import User
from utilities.generator import default_pid_generator, primary_key_generator, public_id_generator


class Staff(models.Model):
    "The client model. Which is also a subclass of Base User."
    id = models.UUIDField(
        primary_key=True,
        default=primary_key_generator,
        editable=False,
        max_length=100,
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="staff_profile"
    )
    public_id = models.CharField(max_length=50, db_index=True, default=partial(default_pid_generator, "STAFF"))

    def __str__(self) -> str:
        return self.user.email  # type: ignore
    

    def save(self, *args, **kwargs):
        if (self._state.adding):
            _id = self.id or primary_key_generator()
            self.public_id = public_id_generator(_id, "STAFF")
        return super().save(*args, **kwargs)
