from django.db import models
from utilities.generator import id_generator
from users.models import User


class Review(models.Model):
    """A class that represent the reviews of job-creators"""

    rating = models.IntegerField(default=0)
    content = models.TextField(max_length=500, default="")
    id = models.CharField(
        primary_key=True, default=id_generator, editable=False, max_length=64
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviewer")

    deleted = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return f"<{self.author.username}>: {self.content[:15]}"


class Client(models.Model):
    id = models.CharField(
        primary_key=True, default=id_generator, editable=False, max_length=64
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="client_profile"
    )

    # About
    bio = models.TextField(max_length=1500, default="")
    rating = models.IntegerField(default=0, blank=True, null=False)
    reviews = models.ManyToManyField(Review, blank=True, related_name="client")

    # Personal info
    phone = models.CharField(max_length=50, default="", blank=True)
    phone_code = models.CharField(max_length=10, default="", blank=True)
    country = models.CharField(default="", max_length=100)
    country_code = models.CharField(max_length=10, default="", blank=True)
    state = models.CharField(max_length=50, default="", blank=True)
    district = models.CharField(max_length=50, default="", blank=True)
    city = models.CharField(default="", blank=True, max_length=100)
    zip_code = models.CharField(max_length=20, default="00000", blank=True)

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
        return self.user.username or self.country

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
    def address(self):
        return f"{self.country} | {self.city or self.state}"

    # Calculates the client's average rating
    def calculate_rating(self):
        return (
            self.reviews.select_related().aggregate(rating=models.Avg("rating"))[
                "rating"
            ]
            or 0.0
        )
