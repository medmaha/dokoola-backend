from rest_framework import serializers

from core.serializers import MergeSerializer
from talents.models import Talent


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

    def mini_representation(self, instance: Talent):
        return {
            "public_id": instance.public_id,
            "avatar": instance.user.avatar,
            "name": instance.name,
            "title": instance.title,
        }

    def common_values(self, instance: Talent):
        return {
            "badge": instance.badge,
            "rating": instance.rating,
            "skills": instance.skills,
            "pricing": instance.pricing,
            "public_id": instance.public_id,
            "avatar": instance.user.avatar,
            "name": instance.name,
            "title": instance.title,
            "bio": instance.bio[:300],
        }

    def detailed_representation(self, instance: Talent, is_edit=False):
        data = self.common_values(instance)
        user_fields = (
            "username",
            "email",
            "date_joined",
        )
        for field in user_fields:
            data[field] = getattr(instance.user, field)

        talents_fields = (
            "bits",
            "bio",
            "jobs_completed",
            "deleted_at",
            "updated_at",
        )

        for field in talents_fields:
            data[field] = getattr(instance, field)

        if is_edit:
            data["username"] = instance.user.username

        data["location"] = instance.user.get_location()
        return data

    def to_representation(self, instance: Talent):
        s_type_list = ("mini", "detail", "common")
        s_type = str(self.context.get("r_type", "")).lower()

        if s_type not in s_type_list:
            return self.common_values(instance)

        if s_type == "mini":
            return self.mini_representation(instance)

        if s_type == "detail":
            return self.detailed_representation(instance)

        return self.common_values(instance)
