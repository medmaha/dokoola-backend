from django.db import models

from reviews.models import Review
from utilities.generator import id_generator
from users.models import User


class Client(models.Model):
    id = models.CharField(
        primary_key=True, default=id_generator, editable=False, max_length=64
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="client_profile"
    )

    # About
    bio = models.TextField(max_length=1500, default="")

    # TODO: Delete these fields once we have a proper rating system
    rating = models.IntegerField(default=0, blank=True, null=False)
    reviews = models.ManyToManyField(Review, blank=True, related_name="client")

    # Company info
    website = models.CharField(max_length=1000, default="", blank=True)
    industry = models.CharField(max_length=1000, default="", blank=True)

    # Stats
    jobs_active = models.IntegerField(default=0)
    jobs_created = models.IntegerField(default=0)
    jobs_completed = models.IntegerField(default=0)

    # Misc
    deleted = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.user.username

    @property
    def address(self):
        return ""

    # Calculates the client's average rating
    def calculate_rating(self):
        return (
            self.reviews.select_related().aggregate(rating=models.Avg("rating"))[
                "rating"
            ]
            or 0.0
        )

    @property
    def name(self):
        return self.user.name

    @property
    def email(self):
        return self.user.name
