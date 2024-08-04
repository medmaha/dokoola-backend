from rest_framework import serializers

from .models import Message, Thread


class messagingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["content"]


class MessagingListSerializer(serializers.ModelSerializer):
    from_me = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    def get_from_me(self, instance: Message):
        request = self.context.get("request")

        if request and instance.sender == request.user:
            return True
        return False

    def get_created_at(self, instance: Message):
        return instance.updated_at

    class Meta:
        model = Message
        fields = ["id", "content", "from_me", "created_at"]


class ThreadListSerializer(serializers.ModelSerializer):
    recipient = serializers.SerializerMethodField()
    messaging = serializers.SerializerMethodField()

    def get_recipient(self, instance: Thread):
        return {
            "name": instance.recipient.name,
            "avatar": instance.recipient.avatar,
            "username": instance.recipient.username,
        }

    def get_messaging(self, instance: Thread):
        last_message = instance.messaging.all().latest("created_at")

        if not last_message:
            return [{}]

        return [
            {
                "content": last_message.content,
                "created_at": last_message.created_at,
                "from_me": (instance.owner == last_message.sender),
            }
        ]

    class Meta:
        model = Thread
        fields = ["id", "unique_id", "recipient", "messaging"]
