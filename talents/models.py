from functools import partial
from django.db import models
from django.db.models.manager import Manager

from reviews.models import Review
from users.models import User
from utilities.generator import (
    primary_key_generator,
    public_id_generator,
    default_pid_generator,
)


class Certificate(models.Model):
    name = models.CharField(max_length=200, blank=True)
    organization = models.TextField()
    url = models.URLField()
    date_issued = models.DateField()
    file_url = models.URLField(blank=True, null=True)
    published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    public_id = models.CharField(
        max_length=50,
        db_index=True,
        default=partial(default_pid_generator, "Certificate"),
    )

    def save(self, *args, **kwargs):
        if self._state.adding:
            _id = primary_key_generator()
            self.public_id = public_id_generator(_id, "Certificate")
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Portfolio(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    url = models.URLField()
    image = models.CharField(max_length=2000)

    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    public_id = models.CharField(
        max_length=50,
        db_index=True,
        default=partial(default_pid_generator, "Portfolio"),
    )

    def save(self, *args, **kwargs):
        if self._state.adding:
            _id = primary_key_generator()
            self.public_id = public_id_generator(_id, "Portfolio")
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


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

    public_id = models.CharField(
        max_length=50,
        db_index=True,
        default=partial(default_pid_generator, "Education"),
    )

    def save(self, *args, **kwargs):
        if self._state.adding:
            _id = primary_key_generator()
            self.public_id = public_id_generator(_id, "Education")
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.institution[:25]


class TalentManager(Manager):
    pass


class Talent(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=primary_key_generator,
        editable=False,
        max_length=64,
    )

    public_id = models.CharField(
        max_length=50, db_index=True, default=partial(default_pid_generator, "Talent")
    )

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="talent_profile"
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

    jobs_completed = models.IntegerField(default=0)
    badge = models.CharField(max_length=200, default="basic")
    bits = models.IntegerField(default=60, blank=True)

    objects = TalentManager()

    @property
    def email(self):
        return self.user.email

    @property
    def name(self):
        return self.user.name

    def __str__(self) -> str:
        return self.user.email

    def save(self, *args, **kwargs):
        if self._state.adding:
            _id = self.id or primary_key_generator()
            self.public_id = public_id_generator(_id, "Talent")
        return super().save(*args, **kwargs)
