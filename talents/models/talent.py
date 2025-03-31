from django.db import models

from reviews.models import Review
from utilities.generator import primary_key_generator, public_id_generator

from .certificate import Certificate
from .education import Education
from .portfolio import Portfolio


class Talent(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=primary_key_generator,
        editable=False,
        max_length=64,
    )

    user = models.OneToOneField(
        "users.User", on_delete=models.CASCADE, related_name="talent_profile"
    )

    title = models.CharField(max_length=1500, default="", blank=True)
    bio = models.TextField(max_length=1500, default="", blank=True)

    skills = models.CharField(max_length=1000, default="", blank=True)
    pricing = models.CharField(max_length=20, default="100", blank=True)

    reviews = models.ManyToManyField(Review, blank=True, related_name="talent_reviews")
    education = models.ManyToManyField(Education, related_name="talent", blank=True)
    portfolio = models.ManyToManyField(Portfolio, related_name="talent", blank=True)
    certificates = models.ManyToManyField(
        Certificate, related_name="talent", blank=True
    )

    rating = models.FloatField(default=3.5, blank=True)
    jobs_completed = models.IntegerField(default=0)
    badge = models.CharField(max_length=200, default="basic")
    bits = models.IntegerField(default=60, blank=True)

    dob = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    public_id = models.CharField(max_length=50, db_index=True, blank=True)

    PUBLIC_ID_PREFIX = "TAL"

    def save(self, *args, **kwargs):
        if self._state.adding or not self.public_id:
            _id = self.pk or primary_key_generator()
            self.public_id = public_id_generator(_id, self.PUBLIC_ID_PREFIX)
        return super().save(*args, **kwargs)

    @property
    def email(self):
        return self.user.email

    @property
    def name(self):
        return self.user.name

    def average_rating(self):
        """Calculates the client's average rating"""
        default_rating = 3.6
        return (
            self.reviews.aggregate(rating=models.Avg("rating"))["rating"]
            or default_rating
        )

    def __str__(self) -> str:
        return str(self.user.email)
