# create a u serializer class
from django.db.models import Avg, Sum
from rest_framework import serializers
from jobs.models import Job
from users.models import User
from users.serializer import UserSerializer

from .models import Client, Review


class ClientSerializer(serializers.ModelSerializer):
    """
    A serializer for the client list api view
    Use to get the list of clients without much extra information
    """

    user = UserSerializer()

    class Meta:
        model = Client
        fields = ("id", "bio", "jobs_completed", "user")

    def to_representation(self, instance: Client):
        # TODO: return all necessary fields
        representation = super().to_representation(instance)
        representation["date_joined"] = instance.user.date_joined

        try:
            user_data = representation.pop("user")
            representation = {**user_data, **representation}
        except KeyError:
            pass
        return representation


class ClientUpdateDataSerializer(serializers.ModelSerializer):
    """
    A readonly serializer for retrieving the updatable data of a client

    """

    class Meta:
        model = Client
        fields = []

    def to_representation(self, instance: Client):
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
            "date_joined": instance.user.date_joined,
        }


class ClientUpdateSerializer(serializers.ModelSerializer):
    """
    This serializer is used for the client update view
    Expose the client's updatable fields
    """

    class Meta:
        model = Client
        fields = (
            "bio",
            "phone",
            "phone_code",
            # Country Info
            "country",
            "country_code",
            "state",
            "district",
            "city",
            "zip_code",
            # Company Info
            "website",
            "industry",
        )


class ClientDetailSerializer(serializers.ModelSerializer):
    """
    A serializer for the client detail api view \n
    Securely serialize all the necessary information of this client
    * The return data will vary depending on the requesting user
    """

    user = UserSerializer()

    class Meta:
        model = Client
        fields = ("bio", "country", "address", "jobs_completed", "user")
        read_only_fields = ["*"]

    def to_representation(self, instance: Client):
        representation = super().to_representation(instance)
        representation["date_joined"] = instance.user.date_joined
        try:
            user_data = representation.pop("user")
            representation = {
                **user_data,
                **representation,
            }
        except KeyError:
            pass
        return representation


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "rating", "content")

    def to_representation(self, instance: Review):
        data = super().to_representation(instance)
        data["author"] = (
            {
                "username": instance.author.username,
                "avatar": instance.author.avatar,
                "name": instance.author.name,
            }
            if instance.author
            else None
        )


class ClientJobDetailSerializer(serializers.ModelSerializer):
    """
    This serializer is used for the job detail view
    * The return data will vary depending on the requesting user
    """

    class Meta:
        model = Client
        fields = (
            "bio",
            "rating",
            "reviews",
            "country",
            "address",
            "jobs_active",
            "jobs_created",
            "jobs_completed",
        )

    # Gets the client's basic user information and returns it
    def user_info(self, user: User):
        return {
            "avatar": user.avatar,
            "name": user.name,
            "username": user.username,
        }

    # Calculate how much this client has been spent on jobs
    def calculate_spent(self, instance: Client):
        # get the all jobs created by this client
        completed_jobs = Job.objects.select_related().filter(
            client=instance, completed=True
        )
        return completed_jobs.aggregate(Sum("budget"))["budget__sum"] or 0

    def to_representation(self, instance: Client):

        representation = super().to_representation(instance)
        representation["rating"] = instance.calculate_rating()
        representation["date_joined"] = instance.user.date_joined
        representation["total_spent"] = self.calculate_spent(instance)
        representation.update(self.user_info(instance.user))

        return representation
