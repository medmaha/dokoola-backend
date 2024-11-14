from rest_framework import serializers
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from users.models.ott import OTT, OTTProxy


class VerifyOttAPIView(GenericAPIView):
    permission_classes = ()
    authentication_classes = ()

    def get_serializer_class(self):
        class Serializer(serializers.ModelSerializer):
            class Meta:
                model = OTT
                fields = ("code",)

        return Serializer

    def post(self, request, *args, **kwargs):
        code = request.data.get("code")
        email = request.data.get("email")
        verified = OTTProxy.validate_ott(email, code)

        if verified:
            OTTProxy.invalidate_ott(email)
            return Response(
                {
                    "verified": True,
                    "message": ("Successfully sent the code"),
                }
            )
        return Response(
            {
                "verified": False,
                "message": "Invalid verification code",
            },
            status=400,
        )
