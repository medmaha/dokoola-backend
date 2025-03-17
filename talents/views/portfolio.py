from django.db import transaction
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from ..models import Portfolio, Talent
from ..serializers import (
    TalentPortfolioSerializer,
)

from utilities.generator import get_serializer_error_message


class TalentPortfolioAPIView(GenericAPIView):
    serializer_class = TalentPortfolioSerializer

    def get(self, request, public_id: str, *args, **kwargs):
        try:
            user = request.user
            
            if user.public_id == public_id:
                portfolio = Portfolio.objects.filter(
                    talent__public_id=public_id
                ).order_by("published", "-updated_at")
            else:
                portfolio = Portfolio.objects.filter(
                    talent__public_id=public_id, published=True
                ).order_by("-updated_at")

            serializer = self.get_serializer(portfolio, many=True)
            return Response(serializer.data, status=200)

        except Exception as e:

            return Response(
                {"message": "Error: Something went wrong!"},
                status=500,
            )

    def post(self, request, public_id: str, *args, **kwargs):
        user = request.user
        profile, profile_name = user.profile

        if profile_name.lower() != "talent":
            return Response({"message": "This request is prohibited"}, status=403)

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            msg = get_serializer_error_message(serializer)
            return Response({"message": msg}, status=400)

        try:
            with transaction.atomic():
                portfolio = serializer.save()
                profile.portfolio.add(portfolio)
                return Response(serializer.data, status=200)

        except:
            return Response(
                {"message": "Error: Something went wrong!"},
                status=500,
            )

    def put(self, request, public_id: str, *args, **kwargs):
        try:
            portfolio = Portfolio.objects.get(public_id=public_id, talent__user=request.user)
            serializer = self.get_serializer(instance=portfolio, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)

            msg = get_serializer_error_message(serializer)
            raise Exception(msg)
        except Portfolio.DoesNotExist:
            return Response({"message": "This request is prohibited"}, status=403)
        except Exception as e:
            return Response({"message": e}, status=400)

    def delete(self, request, public_id: str, *args, **kwargs):
        try:
            portfolio = Portfolio.objects.get(public_id=public_id, talent__user=request.user)
            portfolio.delete()
            return Response({"message": "Portfolio deleted"}, status=200)
        except Portfolio.DoesNotExist:
            return Response({"message": "This request is prohibited"}, status=403)
        except:
            return Response({"message": "Bad request attempted"}, status=400)
