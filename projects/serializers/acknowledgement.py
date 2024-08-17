from rest_framework import serializers
from projects.models.acknowledgement import Acknowledgement


class AcknowledgementRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acknowledgement
        fields = ("id", "comment", "acknowledged", "created_at")


class AcknowledgementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acknowledgement
        fields = ("comment", "acknowledged")


class AcknowledgementUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acknowledgement
        fields = ("comment", "acknowledged")
