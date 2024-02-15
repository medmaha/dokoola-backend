from django.db import models
from utilities.generator import hex_generator

from users.models import User

class Review(models.Model):
    id = models.CharField(primary_key=True, default=hex_generator, editable=False, max_length=64)
    author = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField(default=5)
    text = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:25]

