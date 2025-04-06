from functools import partial

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from reviews.models import Review
from utilities.generator import (
    default_pid_generator,
    primary_key_generator,
    public_id_generator,
)


class Company(models.Model):
    id = models.UUIDField(
        primary_key=True, default=primary_key_generator, editable=False, max_length=100
    )
    public_id = models.CharField(null=False, blank=True, max_length=100)

    slug = models.CharField(
        max_length=50, db_index=True, default=partial(default_pid_generator, "")
    )

    name = models.CharField(max_length=1000, default="", unique=True)
    description = models.TextField(max_length=1500, default="")

    website = models.CharField(max_length=1000, default="", blank=True)
    industry = models.CharField(max_length=1000, default="", blank=True)

    date_established = models.DateField(null=True, blank=True)

    logo_url = models.CharField(max_length=1000, default="", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self._state.adding or not self.public_id:
            _id = self.pk or primary_key_generator()
            self.public_id = public_id_generator(_id, "C")
        return super().save(*args, **kwargs)


class Client(models.Model):

    id = models.UUIDField(
        primary_key=True, default=primary_key_generator, editable=False, max_length=100
    )

    is_agent = models.BooleanField(default=False)
    public_id = models.CharField(max_length=50, db_index=True)

    user = models.OneToOneField(
        "users.User", on_delete=models.CASCADE, related_name="client_profile"
    )

    company = models.OneToOneField(Company, on_delete=models.SET_NULL, null=True)
    _company = models.JSONField(null=True, blank=True, default=dict)

    # About Me (The Client)
    about = models.TextField(max_length=1500, null=True, blank=True)

    reviews_count = models.IntegerField(default=0, blank=True, null=False)
    reviews = models.ManyToManyField(Review, blank=True, related_name="client")
    rating = models.FloatField(default=0, blank=True, null=False, max_length=5)

    country = models.JSONField(encoder=DjangoJSONEncoder, null=True, max_length=500)
    address = models.CharField(max_length=1000, default="", blank=True)
    logo_url = models.CharField(max_length=1000, default="", blank=True)

    # Misc
    deleted_at = models.DateTimeField(null=True, blank=True)

    PUBLIC_ID_PREFIX = "CL"

    def __str__(self):
        return self.name

    # Calculates the client's average rating
    def average_rating(self, recalculate=False, db_commit=False):
        default_rating = 3.7

        if not recalculate:
            return self.rating or default_rating
        
        rating = float(
            self.reviews.select_related().aggregate(rating=models.Avg("rating"))[
                "rating"
            ]
            or default_rating
        )

        if db_commit and float(self.rating) != rating:
            self.rating = rating
            self.save()

        return rating

    @property
    def name(self):
        if self._company:
            return self._company.get("name")
        return self.user.name
    
    @property
    def logo(self):
        if self._company:
            return self._company.get("logo_url")
        return self.logo_url or self.user.avatar
    


    @property
    def email(self):
        return self.user.name

    def save(self, *args, **kwargs):
        if self._state.adding or not self.public_id:
            _id = self.pk or primary_key_generator()
            self.public_id = public_id_generator(_id, self.PUBLIC_ID_PREFIX)

        if self.company:
            _company = self._company or dict()

            if _company.get("updated_at") != str(self.company.updated_at):
                _company["name"] = self.company.name
                _company["slug"] = self.company.slug
                _company["logo_url"] = self.company.logo_url
                _company["updated_at"] = str(self.company.updated_at)
                self._company = _company

        return super().save(*args, **kwargs)
