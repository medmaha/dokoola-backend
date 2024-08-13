from users.models.ott import OTTProxy
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView


class VerifyOttAPIView(GenericAPIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        code = request.data.get("code")
        email = request.data.get("email")
        print(email, code)
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
