from django.db import models

from users.models import User
from utilities.generator import id_generator


class Staff(models.Model):
    "The client model. Which is also a subclass of Base User."
    id = models.CharField(
        primary_key=True, default=id_generator, editable=False, max_length=100
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="staff_profile"
    )

    def __str__(self) -> str:
        return self.user.email  # type: ignore
