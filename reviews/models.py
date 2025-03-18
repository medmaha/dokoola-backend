from django.db import models


class Review(models.Model):
    author = models.ForeignKey(
        "users.User", related_name="user_reviews", on_delete=models.CASCADE
    )
    rating = models.FloatField(default=5)
    text = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.rating}] - {self.text[:25]}"
