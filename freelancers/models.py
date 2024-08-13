from django.db import models
from django.db.models.manager import Manager
from utilities.generator import id_generator
from users.models import User
from reviews.models import Review


class Portfolio(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    url = models.URLField()
    image = models.CharField(max_length=2000)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Education(models.Model):
    course = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    present = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.institution[:25]


class FreelancerManager(Manager):
    pass


class Freelancer(models.Model):
    id = models.CharField(
        primary_key=True, default=id_generator, editable=False, max_length=64
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="freelancer_profile"
    )
    title = models.CharField(max_length=1500, default="", blank=True)
    bio = models.TextField(max_length=1500, default="", blank=True)

    skills = models.CharField(max_length=1000, default="", blank=True)
    education = models.ManyToManyField(Education, related_name="freelancer", blank=True)

    pricing = models.CharField(max_length=20, default="100", blank=True)
    reviews = models.ManyToManyField(
        Review, blank=True, related_name="freelancer_reviews"
    )

    portfolio = models.ManyToManyField(Portfolio, related_name="freelancer", blank=True)

    jobs_completed = models.IntegerField(default=0)
    badge = models.CharField(max_length=200, default="basic")
    bits = models.IntegerField(default=60, blank=True)

    objects = FreelancerManager()

    @property
    def email(self):
        return self.user.email

    @property
    def name(self):
        return self.user.name

    def __str__(self) -> str:
        return self.user.email
