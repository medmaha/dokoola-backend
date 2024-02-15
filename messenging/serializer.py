from rest_framework import serializers

from .models import Messenging, Thread


class MessengingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messenging
        fields = ["content"]


class MessengingListSerializer(serializers.ModelSerializer):
    from_me = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    def get_from_me(self, instance: Messenging):
        request = self.context.get("request")

        if request and instance.sender == request.user:
            return True
        return False

    def get_created_at(self, instance: Messenging):
        return instance.updated_at

    class Meta:
        model = Messenging
        fields = ["id", "content", "from_me", "created_at"]


class ThreadListSerializer(serializers.ModelSerializer):
    recipient = serializers.SerializerMethodField()
    messenging = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    def get_id(self, instance: Thread):
        return instance.unique_id

    def get_recipient(self, instance: Thread):
        return {
            "name": instance.recipient.name,
            "avatar": instance.recipient.avatar,
            "username": instance.recipient.username,
        }

    def get_messenging(self, instance: Thread):
        last_message = instance.messenging.all().latest("created_at")

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
        fields = ["id", "recipient", "messenging"]
