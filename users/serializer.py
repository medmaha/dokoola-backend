# create a u serializer class
from rest_framework import serializers

from .models import User


class AuthUserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = User
        fields = ("avatar", "name", "is_active")

    def to_representation(self, instance: User):
        data = super().to_representation(instance)

        profile, profile_name = instance.profile

        if profile:
            data.update({"profile": profile_name})
        if hasattr(profile, "public_id"):
            data.update({"public_id": profile.public_id})

        if instance.is_staff:
            data.update({"is_staff": True})
        if instance.is_client:
            data.update({"is_client": True})
        if instance.is_talent:
            data.update({"is_talent": True})

        data.update({"is_authenticated": True})
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    profile = serializers.SerializerMethodField(method_name="get_profile")

    def get_profile(self, instance: User):
        [_, name] = instance.profile
        return name

    class Meta:
        model = User
        fields = ("avatar", "name", "username", "profile")


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
            "first_name",
            "last_name",
            "is_active",
            "is_client",
            "is_talent",
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "avatar",
            "first_name",
            "last_name",
            "username",
            "gender",
            "phone",
            "zip_code",
            "email",
        )

    @classmethod
    def merge_serialize(cls, instance, validated_data, metadata: dict = {}, **kwargs):
        data = dict()
        for field in cls.Meta.fields:

            if field in metadata.get("exclude", []):
                data[field] = getattr(instance, field)
                continue

            if field in validated_data:
                data[field] = validated_data[field]
            else:
                data[field] = getattr(instance, field)
        return cls(instance=instance, data=data, **kwargs)
