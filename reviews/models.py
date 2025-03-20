from django.db import models

from users.models import User


class Review(models.Model):
    author = models.ForeignKey(
        User, related_name="user_reviews", on_delete=models.CASCADE
    )
    rating = models.FloatField(default=5)
    text = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_valid = models.BooleanField(default=True)

    def __str__(self):
        return f"[{self.rating}] - {self.text[:25]}"
