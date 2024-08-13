from django.db import models
from users.models import User


def get_default() -> User:
    return User.objects.filter()[0]


class Message(models.Model):

    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messaging_sent"
    )
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messaging_received"
    )
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.content[:20]

    class Meta:
        get_latest_by = "created_at"


class Thread(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="thread_owner"
    )
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="thread_recipient"
    )

    messaging = models.ManyToManyField(Message, related_name="thread")
    # updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    unique_id = models.CharField(max_length=100, default="")

    def __str__(self) -> str:
        return self.owner.username

    class Meta:
        get_latest_by = "created_at"
