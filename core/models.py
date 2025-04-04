from django.db import models


class Waitlist(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    DEFAULT_NAME = "Dear"

    def __str__(self):
        return f"{self.name} - {self.email}"

    def save(self, *args, **kwargs):
        self.name = self.name or self.DEFAULT_NAME
        return super().save(*args, **kwargs)


class Feedback(models.Model):
    message = models.TextField(null=True)
    author_name = models.CharField(max_length=255)
    author_email = models.EmailField(null=True, blank=True)
    likes_count = models.PositiveIntegerField(default=1, blank=True)
    rating = models.IntegerField(default=1, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    blacklisted = models.BooleanField(default=False)


class Category(models.Model):

    is_agent = models.BooleanField(default=False)
    parent = models.ForeignKey(
        "core.Category", on_delete=models.CASCADE, null=True, blank=True
    )

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    keywords = models.TextField()
    image_url = models.TextField()
    description = models.TextField()
    disabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name
