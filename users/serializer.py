# create a u serializer class
from rest_framework import serializers
from .models import User


class AuthUserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    def to_representation(self, instance: User):
        data = super().to_representation(instance)

        if instance.is_staff:
            data.update({"is_staff": True})
        if instance.is_client:
            data.update({"is_client": True})
        if instance.is_freelancer:
            data.update({"is_freelancer": True})

        return data

    class Meta:
        model = User
        fields = (
            "name",
            "avatar",
            "username",
            "is_active",
        )


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
            "is_freelancer",
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
            "country",
            "phone_code",
            "country_code",
            "state",
            "district",
            "zip_code",
            "city",
        )

    def validate_gender(self, value: str):
        if not value:
            raise serializers.ValidationError("Gender cannot be blank")
        value = value.upper()
        return value
