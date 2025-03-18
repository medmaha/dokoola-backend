from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models

from utilities.generator import primary_key_generator, public_id_generator


class Education(models.Model):
    degree = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    location = models.CharField(max_length=200)

    start_date = models.DateField()
    end_date = models.DateField()

    published = models.BooleanField(default=False)
    achievements = models.TextField(max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    public_id = models.CharField(max_length=50, db_index=True, blank=True)

    def save(self, *args, **kwargs):
        if self._state.adding or not self.public_id:
            _id = self.pk or primary_key_generator()
            self.public_id = public_id_generator(_id, "Education")
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.degree + " | " + self.institution[:25]

    def full_clean(self, *args, **kwargs) -> None:

        start_date = self.start_date
        end_date = self.end_date

        if not start_date:
            raise ValidationError(
                {
                    "start_date": "Start date is required",
                }
            )

        if start_date > end_date:
            raise ValidationError(
                {"start_date": "Start date cannot be later than end date"}
            )

        if start_date > datetime.now().date():
            raise ValidationError({"start_date": "Start date cannot be in the future"})

        if end_date and end_date > datetime.now().date():
            raise ValidationError({"end_date": "End date cannot be in the future"})

        return super().full_clean(*args, **kwargs)
