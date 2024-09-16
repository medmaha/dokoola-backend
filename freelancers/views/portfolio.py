from django.db import transaction

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response


from ..serializers import (
    FreelancerPortfolioSerializer,
)


from ..models import Freelancer, Portfolio


class FreelancerPortfolioAPIView(GenericAPIView):
    serializer_class = FreelancerPortfolioSerializer

    def get(self, request, username: str, *args, **kwargs):
        try:
            portfolio = (
                Freelancer.objects.get(user__username=username)
                .portfolio.filter()
                .order_by("-updated_at")
            )
            serializer = self.get_serializer(portfolio, many=True)
            return Response(serializer.data, status=200)
        except Freelancer.DoesNotExist:
            return Response({"message": "This request is prohibited"}, status=403)

        except Exception as e:

            return Response(
                {"message": "Error: Something went wrong!"},
                status=500,
            )

    def post(self, request, username: str, *args, **kwargs):
        user = request.user
        profile, profile_name = user.profile

        if not profile_name.lower() == "freelancer":
            return Response({"message": "This request is prohibited"}, status=403)

        serializer = self.get_serializer(data=request.data)

        try:
            with transaction.atomic():
                if serializer.is_valid():
                    portfolio = serializer.save()
                    profile.portfolio.add(portfolio)
                    return Response(serializer.data, status=200)

                return Response({"message": "Bad request attempted"}, status=400)
        except:
            return Response(
                {"message": "Error: Something went wrong!"},
                status=500,
            )

    def put(self, request, username: str, *args, **kwargs):
        try:
            pid = request.data.get("pid")
            portfolio = Portfolio.objects.get(id=pid, freelancer__user=request.user)
            serializer = self.get_serializer(instance=portfolio, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            raise Exception(str(serializer.errors))
        except Portfolio.DoesNotExist:
            return Response({"message": "This request is prohibited"}, status=403)
        except Exception as e:
            return Response({"message": str(e)}, status=400)

    def delete(self, request, username: str, *args, **kwargs):
        try:
            pid = request.data.get("pid")
            portfolio = Portfolio.objects.get(id=pid, freelancer__user=request.user)
            portfolio.delete()
            return Response({"message": "Portfolio deleted"}, status=200)
        except Portfolio.DoesNotExist:
            return Response({"message": "This request is prohibited"}, status=403)
        except:
            return Response({"message": "Bad request attempted"}, status=400)
