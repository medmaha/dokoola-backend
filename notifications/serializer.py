from rest_framework import serializers

from .models import Notification
from users.serializer import UserSerializer


class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer()

    class Meta:
        model = Notification
        fields = ["id", "created_at", "is_seen", "sender", "hint_text", "content_text"]
