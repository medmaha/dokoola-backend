from django.db import models

from users.models import User


class Notification(models.Model):

    sender = models.ForeignKey(
        User,
        related_name="notification_sender",
        on_delete=models.SET_NULL,
        null=True,
    )
    recipient = models.ForeignKey(
        User,
        related_name="notification_recipient",
        on_delete=models.CASCADE,
    )

    hint_text = models.CharField(max_length=300, default="")
    content_text = models.CharField(max_length=1000, default="")
    object_api_link = models.CharField(max_length=1000, null=True, blank=True)

    is_seen = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    type = models.CharField(null=True, blank=True, max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hint_text
