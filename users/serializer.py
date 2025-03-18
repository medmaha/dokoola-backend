# create a u serializer class
from rest_framework import serializers

from talents.serializers.base import MergeSerializer

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    profile = serializers.SerializerMethodField(method_name="get_profile")

    def get_profile(self, instance: User):
        [_, name] = instance.profile
        return name

    class Meta:
        model = User
        fields = ("avatar", "name", "username", "profile")


class UserWriteSerializer(MergeSerializer, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
            "first_name",
            "last_namt",
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
