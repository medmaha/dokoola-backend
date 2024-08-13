from django.db import models
from core.models import Category
from clients.models import Client
from utilities.generator import hex_generator
from .pricing import Pricing


class JobStatusChoices(models.TextChoices):
    CLOSED = "CLOSED"
    PUBLISHED = "PUBLISHED"
    SUSPENDED = "SUSPENDED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class Job(models.Model):

    slug = models.SlugField(max_length=200, blank=True, default="")

    title = models.CharField(max_length=200)

    description = models.TextField()

    location = models.CharField(max_length=200)

    published = models.BooleanField(default=False, blank=True)

    status = models.CharField(
        max_length=200, choices=JobStatusChoices.choices, default="CLOSED"
    )

    is_valid = models.BooleanField(default=True, blank=True)

    budget = models.DecimalField(max_digits=10, decimal_places=2)

    pricing = models.ForeignKey(
        Pricing, on_delete=models.CASCADE, related_name="job_pricing"
    )

    activities = models.ForeignKey(
        "Activities", on_delete=models.CASCADE, related_name="job"
    )

    duration = models.CharField(max_length=1000, blank=True, null=True)

    required_skills = models.CharField(max_length=1000, blank=True, default="")

    category_obj = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    client = models.ForeignKey(Client, related_name="jobs", on_delete=models.DO_NOTHING)

    updated_at = models.DateTimeField(auto_now=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title[:50]

    @property
    def category(self):
        return self.category_obj.name if self.category_obj else None

    @property
    def payment_type(self):
        payment_type = self.pricing.payment_type.lower()
        fixed_price = self.pricing.fixed_price
        if payment_type.lower() == "project":
            if fixed_price:
                return "per project / fixed price"
            return "per project"
        if fixed_price:
            return "per hour / fixed price"
        return "per hour"

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.slug = hex_generator(16)

        return super().save(*args, **kwargs)
