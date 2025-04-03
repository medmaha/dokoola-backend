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

    def mini_values(self, instance: Talent):
        return {
            "bits": instance.bits,
            "name": instance.name,
            "title": instance.title,
            "avatar": instance.user.avatar,
            "public_id": instance.public_id,
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
            "bits": instance.bits,
        }

    def edit_representation(self, instance: Talent):
        data = self.common_values(instance)
        user_fields = (
            "username",
            "phone",
            "gender",
            "state",
            "district",
            "country",
            "city",
            "zip_code",
            "phone_code",
            "country_code",
        )
        for field in user_fields:
            data[field] = getattr(instance.user, field)

        talents_fields = (
            "bio",
            "dob",
        )

        for field in talents_fields:
            data[field] = getattr(instance, field)

        data["location"] = instance.user.get_location()
        return data

    def detailed_representation(self, instance: Talent):
        data = self.common_values(instance)
        user_fields = ("date_joined",)
        for field in user_fields:
            data[field] = getattr(instance.user, field)

        talents_fields = (
            "bio",
            "jobs_completed",
            "deleted_at",
            "updated_at",
        )

        for field in talents_fields:
            data[field] = getattr(instance, field)

        data["location"] = instance.user.get_location()
        return data

    def to_representation(self, instance: Talent):
        r_type_list = ("mini", "detail", "edit")
        r_type = str(self.context.get("r_type", "")).lower()

        if r_type not in r_type_list or r_type == "mini":
            return self.mini_values(instance)

        if r_type == "edit":
            return self.edit_representation(instance)

        if r_type == "detail":
            return self.detailed_representation(instance)

        return self.common_values(instance)
