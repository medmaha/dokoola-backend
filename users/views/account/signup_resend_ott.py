from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from core.services.email import email_service
from users.models.ott import OTTProxy


class ResendOttAPIView(GenericAPIView):
    permission_classes = ()
    authentication_classes = ()

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

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        self.resend_verification_code(email)
        return Response(
            {
                "message": ("Successfully sent the code"),
            }
        )
