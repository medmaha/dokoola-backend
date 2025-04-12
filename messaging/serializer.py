from rest_framework import serializers

from .models import Message, Thread


class MessagingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["content"]


class MessagingListSerializer(serializers.ModelSerializer):
    sender_id = serializers.SerializerMethodField()

    def get_sender_id(self, instance: Message):
        return instance.sender.public_id

    def to_representation(self, instance):
        response = super().to_representation(instance)
        return response

    class Meta:
        model = Message
        fields = ["id", "content", "created_at", "sender_id"]


class ThreadListSerializer(serializers.ModelSerializer):
    recipient = serializers.SerializerMethodField()
    messaging = serializers.SerializerMethodField()

    def get_recipient(self, instance: Thread):
        return {
            "name": instance.recipient.name,
            "avatar": instance.recipient.avatar,
            "public_id": instance.recipient.public_id,
        }

    def get_messaging(self, instance: Thread):
        last_message: Message = instance.messaging.latest("created_at")

        if not last_message:
            return [{}]
        last_message_data = MessagingListSerializer(instance=last_message).data

        return [last_message_data]

    class Meta:
        model = Thread
        fields = ["id", "unique_id", "recipient", "messaging"]
