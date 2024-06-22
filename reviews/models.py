from typing import Any
from django.db import models
from utilities.generator import hex_generator

from users.models import User


class ReviewManger(models.Manager):

    def filter(self, *args: Any, **kwargs: Any):
        return super().filter(*args, **kwargs).order_by("-created_at__month")

    def values(self, *fields: Any, **expressions: Any):
        return super().values(*fields, **expressions).order_by("-created_at__month")


class Review(models.Model):
    id = models.CharField(
        primary_key=True, default=hex_generator, editable=False, max_length=64
    )
    author = models.ForeignKey(User, related_name="reviews", on_delete=models.CASCADE)
    rating = models.FloatField(default=5)
    text = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)

    object = ReviewManger()

    def __str__(self):
        return self.text[:25]
