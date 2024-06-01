from rest_framework import serializers

from .models import Notification
from users.serializer import UserSerializer


class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer()

    class Meta:
        model = Notification
        fields = [
            "id",
            "sender",
            "is_seen",
            "hint_text",
            "created_at",
            "content_text",
            "object_api_link",
        ]
