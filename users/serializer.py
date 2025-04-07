# create a u serializer class
from rest_framework import serializers

from core.serializers import MergeSerializer

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


class UserSearchSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = User
        fields = ("avatar", "name")


    def to_representation(self, instance:User):
        data = super().to_representation(instance)
        profile = instance.profile

        if profile[1] == "Talent":
            talent = profile[0]
            data.update({
                "title": talent.title,
            })
        elif profile[1] == "Client":
            client = profile[0]
            data.update({
                "company_name": client.name,
            })

        data["rating"] = profile[0].rating
        data["public_id"] = profile[0].public_id
        data["profile_type"] = profile[1]
        data["date_joined"] = instance.date_joined

        return data



class UserWriteSerializer(MergeSerializer, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "phone",
            "gender",
            "state",
            "district",
            "country",
            "city",
            "zip_code",
            "phone_code",
            "country_code",
        ]


class UserUpdateSerializer(MergeSerializer, serializers.ModelSerializer):
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
