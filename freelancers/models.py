from django.db import models
from django.db.models.manager import Manager
from utilities.generator import id_generator
from users.models import User
from reviews.models import Review


class Education(models.Model):
    course = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    present = models.BooleanField(default=False)

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

    # Personal info
    phone = models.CharField(max_length=50, default="", blank=True)
    phone_code = models.CharField(max_length=10, default="", blank=True)
    country = models.CharField(default="", max_length=100)
    country_code = models.CharField(max_length=10, default="", blank=True)
    state = models.CharField(max_length=50, default="", blank=True)
    district = models.CharField(max_length=50, default="", blank=True)
    city = models.CharField(default="", blank=True, max_length=100)
    zip_code = models.CharField(max_length=20, default="00000", blank=True)

    pricing = models.CharField(max_length=20, default="100", blank=True)
    reviews = models.ManyToManyField(
        Review, blank=True, related_name="freelancer_reviews"
    )

    jobs_completed = models.IntegerField(default=0)
    badge = models.CharField(max_length=200, default="basic")
    bits = models.IntegerField(default=60, blank=True)

    objects = FreelancerManager()

    def __str__(self) -> str:
        return self.user.email

    def get_address(self):
        """Returns the client's address in a dictionary format"""
        return {
            "zip_code": self.zip_code,
            "country": self.country,
            "country_code": self.country_code,
            "phone_code": self.phone_code,
            "state": self.state,
            "district": self.district,
            "city": self.city,
        }

    def get_location(self):
        return f"{self.country} | {self.city or self.state}"

    @property
    def location(self):
        return f"{self.country} | {self.city or self.state}"

    def calculate_rating(self):
        return (
            self.reviews.select_related().aggregate(rating=models.Avg("rating"))[
                "rating"
            ]
            or 0.0
        )
