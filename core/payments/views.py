from rest_framework.generics import GenericAPIView
from rest_framework.response import Response


class Payment(GenericAPIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        payment_data = {
            "amount": request.data.get("amount"),
            "currency": request.data.get("currency", "GMD"),
        }
