import uuid

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from reviews.models import Review
from users.models import User


class Company(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=64
    )

    name = models.CharField(max_length=1000, default="", unique=True)
    slug = models.SlugField(
        max_length=1000, default="", null=True, blank=True, unique=True
    )
    description = models.TextField(max_length=1500, default="")

    website = models.CharField(max_length=1000, default="", blank=True)
    industry = models.CharField(max_length=1000, default="", blank=True)

    date_established = models.DateField(null=True, blank=True)

    logo_url = models.CharField(max_length=1000, default="", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # TODO: add many fields as necessary

    deleted_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Client(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=64
    )

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="client_profile"
    )

    company = models.OneToOneField(Company, on_delete=models.SET_NULL, null=True)

    # About Me (The Client)
    about = models.TextField(max_length=1500, null=True, blank=True)

    reviews_count = models.IntegerField(default=0, blank=True, null=False)
    reviews = models.ManyToManyField(Review, blank=True, related_name="client")

    country = models.JSONField(encoder=DjangoJSONEncoder, null=True, max_length=500)
    address = models.CharField(max_length=1000, default="", blank=True)

    # Misc
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    # Calculates the client's average rating
    def average_rating(self):
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
