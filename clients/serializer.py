from django.db.models import Sum
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
            **instance.user.get_personal_info(),
            # Address Info
            **instance.user.get_address(),
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
            "website",
            "industry",
        )

    def update(self, instance, validated_data):
        # Loop through each field and set the current instance value if a value is not passed in
        for field, value in validated_data.items():
            setattr(
                instance,
                field,
                value if value is not None else getattr(instance, field),
            )
        instance.save()
        return instance

    def validate_bio(self, value):
        if not value:
            raise serializers.ValidationError("Your bio cannot be empty")
        return value


class ClientDetailSerializer(serializers.ModelSerializer):
    """
    A serializer for the client detail api view \n
    Securely serialize all the necessary information of this client
    * The return data will vary depending on the requesting user
    """

    class Meta:
        model = Client
        fields = ("bio", "jobs_completed")
        read_only_fields = ["*"]

    def to_representation(self, instance: Client):
        representation = super().to_representation(instance)
        representation["date_joined"] = instance.user.date_joined
        representation.update(
            {
                "avatar": instance.user.avatar,
                "name": instance.user.name,
                "username": instance.user.username,
                **instance.user.get_personal_info(),
            }
        )
        try:
            user_data = representation.pop("user")
            representation = {
                **user_data,
                **representation,
            }
        except KeyError:
            pass
        return representation


class ClientProfileDetailSerializer(serializers.ModelSerializer):
    """
    A serializer for the client detail api view \n
    Securely serialize all the necessary information of this client
    * The return data will vary depending on the requesting user
    """

    class Meta:
        model = Client
        fields = [
            "bio",
            "website",
            "industry",
            "jobs_active",
            "jobs_created",
            "jobs_completed",
        ]

    def get_address(self, instance: Client):
        request = self.context.get("request")
        user = request.user if request else None
        if user and user.pk == instance.user.pk:
            return instance.user.get_address()
        return instance.address

    def to_representation(self, instance: Client):
        data = super().to_representation(instance)
        user: dict = UserSerializer(instance=instance.user).data  # type: ignore
        data.update(user)
        data.update({"rating": instance.calculate_rating()})
        data.update({"address": self.get_address(instance)})
        data.update({"reviews": []})
        return data


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
