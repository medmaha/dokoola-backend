from rest_framework import serializers

from users.serializer import UserSerializer

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    def get_sender(self, instance: Notification):
        if instance.sender:
            return {
                "name": instance.sender.name,
                "public_id": instance.sender.public_id,
                "avatar": instance.sender.avatar,
            }
        else:
            return None

    class Meta:
        model = Notification
        fields = [
            "id",
            "sender",
            "is_seen",
            "hint_text",
            "archived",
            "created_at",
            "content_text",
            "object_api_link",
        ]
