from rest_framework import serializers

from users.models import User
from utilities.privacy import mask_email


class AuthUserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = User
        fields = ("avatar", "name", "is_active", "email_verified")

    def to_representation(self, instance: User):
        data = super().to_representation(instance)

        data["public_id"] = instance.public_id
        data["email"] = mask_email(instance.email)

        if instance.is_staff:
            data.update({"is_staff": True, "profile_type": "Staff"})
        if instance.is_client:
            data.update({"is_client": True, "profile_type": "Client"})
        if instance.is_talent:
            data.update({"is_talent": True, "profile_type": "Talent"})

        return data
