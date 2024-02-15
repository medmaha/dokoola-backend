from django.db import models
from utilities.generator import hex_generator

from clients.models import Client
from django.utils.text import slugify


class Pricing(models.Model):
    fixed_price = models.BooleanField(default=True, blank=True)
    negotiable_price = models.BooleanField(default=False, blank=True)
    will_pay_more = models.BooleanField(default=False, blank=True)
    addition = models.CharField(max_length=100)
    payment_type = models.CharField(max_length=100, default="PROJECT")


class Job(models.Model):
    id = models.CharField(
        primary_key=True, default=hex_generator, editable=False, max_length=64
    )
    slug = models.SlugField(max_length=200, blank=True, default="")

    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    active_state = models.BooleanField(default=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    pricing = models.ForeignKey(
        Pricing, on_delete=models.CASCADE, related_name="job_pricing"
    )
    activities = models.ForeignKey(
        "Activities", on_delete=models.CASCADE, related_name="job"
    )
    category = models.CharField(max_length=1000, blank=True, default="")
    required_skills = models.CharField(max_length=1000, blank=True, default="")

    client = models.ForeignKey(Client, related_name="jobs", on_delete=models.DO_NOTHING)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title[:50]

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{hex_generator(6)}-") + slugify(self.title[:16])
        return super(Job, self).save(*args, **kwargs)

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


from proposals.models import Proposal


class Activities(models.Model):
    proposals = models.ManyToManyField(Proposal, related_name="job_proposals")
