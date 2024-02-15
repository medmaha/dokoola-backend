# create a u serializer class
import random
from rest_framework import serializers
from .models import Freelancer
from users.serializer import UserSerializer


class FreelancerMiniSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = Freelancer
        fields = []

    def to_representation(self, instance):
        return {
            "username": instance.user.username,
            "avatar": instance.user.avatar,
            "name": instance.user.name,
        }


class FreelancerSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    ratings = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()

    class Meta:
        model = Freelancer
        fields = ("bio", "badge", "skills", "title", "pricing", "ratings", "location")

    def get_ratings(self, instance):
        [prefix, suffix] = str(random.uniform(0.50, 5)).split(".")
        suffix = suffix[0]
        return f"{prefix}.{suffix}0"

    def get_skills(self, instance):
        skills = instance.skills.split(",")

        if len(skills) and skills[0]:
            return skills
        return []

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = UserSerializer(instance=instance.user).data

        return {**user, **data}


class FreelancerDetailSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = Freelancer
        fields = ("bio", "badge", "pricing", "location")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = UserSerializer(instance=instance.user).data

        return {**user, **data}


class FreelancerUpdateSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = Freelancer
        fields = ("bio", "phone", "city", "address", "zip_code", "country", "city")
