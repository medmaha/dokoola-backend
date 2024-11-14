from rest_framework import serializers
from rest_framework.generics import GenericAPIView

from core.services.email import email_service
from users.models.ott import OTTProxy, OTT


class ResendOttAPIView(GenericAPIView):
    permission_classes = ()
    authentication_classes = ()

    def get_serializer_class(self):
        class Serializer(serializers.ModelSerializer):
            class Meta:
                model = OTT
                fields = ("code",)

        return Serializer

    def resend_verification_code(self, email):
        ott = OTTProxy.generate_ott(identifier=email)
        template_name = "users/email_verification.html"
        text = f"Please use the following code to verify your email address: {ott.code}"
        html_context = {"code": ott.code}

        # TODO: Add callback function to send email
        email_service.send(
            email=email,
            text=text,
            subject="Email Verification",
            html_template_name=template_name,
            html_template_context=html_context,
        )

        return ott

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        ott = self.resend_verification_code(email)
        serializer = self.get_serializer(instance=ott)

        return Response(
            {
                **serializer.data,
                "message": ("Successfully sent the code"),
            }
        )
