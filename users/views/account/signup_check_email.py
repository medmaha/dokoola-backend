from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from core.services.email import email_service
from users.models import User
from users.models.ott import OTTProxy
from utilities.privacy import mask_email


class SignupCheckEmailAPIView(GenericAPIView):
    permission_classes = ()
    authentication_classes = ()

    def get_serializer_class(self):
        class Serializer(serializers.ModelSerializer):
            class Meta:
                model = User
                fields = ("email",)

        return Serializer

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        exists = User.objects.select_related("email").filter(email=email).exists()

        if not exists:
            ott = OTTProxy.generate_ott(identifier=email)
            email_service.send(
                email=email,
                subject="Email Verification",
                text=f"Please use the following code to verify your email address: {ott.code}",
                html_template_name="users/email_verification.html",
                html_template_context={"code": ott.code},
            )

        return Response(
            {
                "exists": exists,
                "email": mask_email(email),
                "message": (
                    "An account with this email already exist"
                    if exists
                    else "No account with this email"
                ),
            },
            status=400 if exists else 200,
        )
