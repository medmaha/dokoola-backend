from django.db import transaction
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from users.models.user import User
from utilities.generator import get_serializer_error_message

from ..models import Portfolio
from ..serializers import TalentPortfolioReadSerializer, TalentPortfolioWriteSerializer


class TalentPortfolioAPIView(GenericAPIView):

    def get(self, request, public_id: str):
        self.serializer_class = TalentPortfolioReadSerializer

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
            # TODO: log error
            return Response(
                {"message": "Error: Something went wrong!"},
                status=500,
            )

    def post(
        self,
        request,
        public_id,
    ):
        self.serializer_class = TalentPortfolioWriteSerializer

        try:
            user: User = request.user
            profile, profile_name = user.profile

            with transaction.atomic():

                if profile_name.lower() != "talent":
                    return Response(
                        {"message": "This request is prohibited"}, status=403
                    )

                serializer = self.get_serializer(data=request.data)

                if not serializer.is_valid():
                    msg = get_serializer_error_message(serializer.errors)
                    return Response({"message": msg}, status=400)

                _portfolio = serializer.save()
                _serializer = TalentPortfolioReadSerializer(_portfolio)
                profile.portfolio.add(_portfolio)
                return Response(_serializer.data, status=201)

        except AssertionError as e:
            return Response({"message": str(e)}, status=403)

        except Exception as e:
            # TODO: log error
            return Response({"message": str(e)}, status=500)

    def put(self, request, public_id: str):
        self.serializer_class = TalentPortfolioWriteSerializer

        try:
            with transaction.atomic():
                portfolio_public_id = request.data.get("public_id")
                portfolio = Portfolio.objects.get(
                    public_id=portfolio_public_id,
                    talent__user=request.user,
                    talent__public_id=public_id,
                )

                serializer = TalentPortfolioWriteSerializer.merge_serialize(
                    portfolio, request.data
                )
                if serializer.is_valid():
                    _portfolio = serializer.save()
                    _serializer = TalentPortfolioReadSerializer(instance=_portfolio)
                    return Response(_serializer.data, status=200)

                msg = get_serializer_error_message(serializer.errors)
                return Response({"message": msg}, status=400)

        except Portfolio.DoesNotExist:
            # TODO: log error
            return Response({"message": "This request is prohibited"}, status=403)

        except AssertionError as e:
            # TODO: log error
            return Response({"message": str(e)}, status=403)

        except Exception as e:
            # TODO: log error
            return Response({"message": str(e)}, status=500)

    def delete(self, request, public_id: str):
        try:
            portfolio_public_id = request.data.get("public_id", None)
            portfolio = Portfolio.objects.get(
                public_id=portfolio_public_id,
                talent__user=request.user,
                talent__public_id=public_id,
            )
            portfolio.delete()
            return Response({"message": "Portfolio deleted"}, status=204)
        except Portfolio.DoesNotExist:
            return Response({"message": "This request is prohibited"}, status=403)
        except:
            return Response({"message": "Bad request attempted"}, status=400)
