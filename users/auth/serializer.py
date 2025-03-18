from rest_framework import serializers

from users.models import User


class AuthUserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = User
        fields = ("avatar", "name", "is_active")

    def to_representation(self, instance: User):
        data = super().to_representation(instance)

        data["public_id"] = instance.public_id

        if instance.is_staff:
            data.update({"is_staff": True})
        if instance.is_client:
            data.update({"is_client": True})
        if instance.is_talent:
            data.update({"is_talent": True})

        return data
