# create a u serializer class
from rest_framework import serializers
from users.serializer import UserSerializer

from .models import Client


class ClientMiniSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = Client
        fields = []

    def to_representation(self, instance):
        return {
            "username": instance.user.username,
            "avatar": instance.user.avatar,
            "name": instance.user.name,
        }


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    user = UserSerializer()

    class Meta:
        model = Client
        fields = ("id", "about", "jobs_completed", "user")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            user_data = representation.pop("user")
            representation = {**user_data, **representation}
        except KeyError:
            pass
        return representation


class ClientDetailSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    user = UserSerializer()

    class Meta:
        model = Client
        fields = ("id", "about", "jobs_completed", "user")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            user_data = representation.pop("user")
            representation = {**user_data, **representation}
        except KeyError:
            pass
        return representation


class ClientUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating a user object"""

    class Meta:
        model = Client
        fields = ("about", "phone", "city", "address", "zip_code", "country", "city")
