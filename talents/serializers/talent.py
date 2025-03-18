from rest_framework import serializers

from talents.models import Talent

from .base import MergeSerializer


class TalentWriteSerializer(MergeSerializer, serializers.ModelSerializer):
    """
    Serializer for updating the talent object
    """

    class Meta:
        model = Talent
        fields = [
            "bio",
            "title",
            "skills",
            "pricing",
        ]


class TalentReadSerializer(serializers.ModelSerializer):
    """
    Serializer for listing the user objects
    """

    class Meta:
        model = Talent
        fields = []

    def common_values(self, instance: Talent):
        return {
            "public_id": instance.public_id,
            "avatar": instance.user.avatar,
            "name": instance.name,
            "title": instance.title,
        }

    def mini_representation(self, instance: Talent):
        # re-populate the data

        return {**self.common_values(instance), "badge": instance.badge}

    def detailed_representation(self, instance: Talent):
        data = super().to_representation(instance)
        data.update(self.common_values(instance))

        user_fields = (
            # "avatar",
            # "username",
            "date_joined",
        )
        for field in user_fields:
            data[field] = getattr(instance.user, field)

        talents_fields = (
            "bits",
            "bio",
            "badge",
            "skills",
            "pricing",
            "jobs_completed",
            "deleted_at",
            "updated_at",
        )

        for field in talents_fields:
            data[field] = getattr(instance, field)

        data["rating"] = instance.average_rating()
        data["location"] = instance.user.get_location()

        return data

    def to_representation(self, instance: Talent):

        serializer_type = self.context.get("s_type") if self.context else None

        if serializer_type == "mini":
            return self.mini_representation(instance)
        if serializer_type == "detail":
            return self.detailed_representation(instance)

        return self.common_values(instance)
