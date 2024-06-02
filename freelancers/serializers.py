# create a u serializer class
import random
from rest_framework import serializers
from .models import Freelancer, Portfolio
from users.serializer import UserSerializer


class FreelancerMiniSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = Freelancer
        fields = []

    def to_representation(self, instance: Freelancer):
        return {
            "username": instance.user.username,
            "avatar": instance.user.avatar,
            "name": instance.user.name,
            "rating": instance.calculate_rating(),
        }


class FreelancerSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    rating = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()

    class Meta:
        model = Freelancer
        fields = ("bio", "badge", "skills", "title", "pricing", "rating", "location")

    def get_rating(self, instance: Freelancer):
        return instance.calculate_rating()

    def get_skills(self, instance):
        skills = instance.skills.split(",")

        if len(skills) and skills[0]:
            return skills
        return []

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user: User = UserSerializer(instance=instance.user).data  # type: ignore

        return {**user, **data}


class FreelancerUpdateDataSerializer(serializers.ModelSerializer):
    """
    A readonly serializer for retrieving the updatable data of a freelancer
    """

    class Meta:
        model = Freelancer
        fields = []

    def to_representation(self, instance: Freelancer):
        return {
            # Client Info
            "bio": instance.bio,
            "phone": instance.phone,
            # Address Info
            **instance.get_address(),
            # User Info
            "email": instance.user.email,
            "name": instance.user.name,
            "avatar": instance.user.avatar,
            "gender": instance.user.gender,
            "username": instance.user.username,
            "first_name": instance.user.first_name,
            "last_name": instance.user.last_name,
            "pricing": instance.pricing,
            "skills": instance.skills.split(",") if instance.skills else [],
            "date_joined": instance.user.date_joined,
        }


class FreelancerUpdateSerializer(serializers.ModelSerializer):
    """
    This serializer is used for the freelancer update view
    Exposes the freelancer's updatable fields
    """

    class Meta:
        model = Freelancer
        fields = (
            "title",
            "bio",
            "phone",
            "phone_code",
            "country",
            "country_code",
            "state",
            "district",
            "city",
            "zip_code",
            "pricing",
        )


class FreelancerMiniInfoSerializer(serializers.ModelSerializer):
    """
    An Serializer for the freelancer information
    """

    class Meta:
        model = Freelancer
        fields = ("id", "bits", "pricing", "location", "skills")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["pricing"] = float(data["pricing"])
        data["skills"] = data.get("skills", "").split(", ")
        return data


class FreelancerDetailSerializer(serializers.ModelSerializer):
    """
    An API View for the freelancer data statistics
    """

    class Meta:
        model = Freelancer
        fields = ("bio", "badge", "pricing", "location")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user: dict = UserSerializer(instance=instance.user).data  # type: ignore

        return {**user, **data}


class FreelancerProfileDetailSerializer(serializers.ModelSerializer):
    """
    An serializer class for the freelancer profile page
    """

    class Meta:
        model = Freelancer
        fields = [
            "bio",
            "title",
            "badge",
            "skills",
            "pricing",
            "jobs_completed",
        ]

    def get_address(self, instance: Freelancer):
        request = self.context.get("request")
        user = request.user if request else None
        if user and user.pk == instance.user.pk:
            return instance.get_address()
        return instance.location

    def to_representation(self, instance: Freelancer):
        data = super().to_representation(instance)
        user: dict = UserSerializer(instance=instance.user).data  # type: ignore
        data.update(user)
        data.update({"rating": instance.calculate_rating()})
        data.update({"address": self.get_address(instance)})
        data.update({"reviews": []})
        data.update({"education": []})
        return data


class FreelancerPortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = "__all__"

    def is_valid(self, *, raise_exception=False):
        self.initial_data = {
            "url": self.initial_data.get("url"),
            "name": self.initial_data.get("name"),
            "image": self.initial_data.get("image"),
            "description": self.initial_data.get("description"),
        }
        return super().is_valid(raise_exception=raise_exception)


class FreelancerPortfolioCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ("image", "title", "description", "url")
