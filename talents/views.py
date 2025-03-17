from django.db import transaction
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.response import Response

from proposals.models import Proposal
from proposals.serializers import ProposalPendingListSerializer

from .dashboard import TalentDashboardSerializer
from .models import Portfolio, Talent
from .search import TalentsSearchAPIView
from .serializers import (
    TalentRetrieveSerializer,
    TalentMiniInfoSerializer,
    TalentPortfolioReadSerializer,
    TalentSerializer,
    TalentUpdateDataSerializer,
    TalentUpdateSerializer,
)


class TalentListAPIView(ListAPIView):
    permission_classes = []

    serializer_class = TalentSerializer

    def get_queryset(self):
        return TalentsSearchAPIView.make_query(self.request.query_params).order_by("badge")  # type: ignore

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={"request": request})

        return self.get_paginated_response(serializer.data)


class TalentUpdateAPIView(GenericAPIView):
    """
    This view is used for the client mini api view
    Retrieves clients updatable information
    """

    permission_classes = []

    def get(self, request, public_id, **kwargs):
        self.serializer_class = TalentUpdateDataSerializer
        try:
            talent = Talent.objects.get(public_id=public_id)
            talent_serializer: TalentUpdateDataSerializer = self.get_serializer(
                instance=talent, context={"request": request}
            )

            return Response(talent_serializer.data, status=200)
        except Talent.DoesNotExist:
            return Response(
                {"message": "Error: User doesn't exist!"},
                status=404,
            )

    def put(self, request, public_id, **kwargs):
        self.serializer_class = TalentUpdateSerializer
        try:
            client = Talent.objects.get(public_id=public_id)
            client_serializer: TalentUpdateSerializer = self.get_serializer(
                instance=client,
                data=request.data,
                context={"request": request},
            )

            if not client_serializer.is_valid():
                # raised the same error as the serializer
                return Response(str(client_serializer.errors), status=400)
            client_serializer.save()
            return Response(client_serializer.data, status=200)
        except Talent.DoesNotExist:
            return Response(
                {"message": "Error: User doesn't exist!"},
                status=404,
            )
        except Exception:

            return Response(
                {"message": "Error: Something went wrong!"},
                status=500,
            )


class FreelanceMiniInfoView(RetrieveAPIView):
    permission_classes = []
    serializer_class = TalentMiniInfoSerializer

    def retrieve(self, request, public_id, **kwargs):
        talent = Talent.objects.filter(public_id=public_id).first()

        if not talent:
            return Response({"message": "This request is prohibited"}, status=403)

        serializer = self.get_serializer(talent)

        return Response(serializer.data, status=200)


class TalentetrieveAPIView(RetrieveAPIView):
    serializer_class = TalentRetrieveSerializer

    def retrieve(self, request, *args, **kwargs):
        public_id = self.kwargs.get("public_id")
        talent = Talent.objects.filter(public_id=public_id).first()

        if not talent:
            return Response({"message": "This request is prohibited"}, status=403)

        serializer = self.get_serializer(talent)

        return Response(serializer.data, status=200)


class TalentProjectsList(ListAPIView):
    serializer_class = ProposalPendingListSerializer

    def get_queryset(self, public_id: str):
        try:
            talent = Talent.objects.select_related().get(public_id=public_id)
        except Talent.DoesNotExist:
            return None
        proposals = Proposal.objects.filter(job__is_valid=True, talent=talent)
        return proposals

    def list(self, request, public_id, *args, **kwargs):
        queryset = self.get_queryset(public_id)
        if not queryset:
            return Response({"message": "This request is prohibited"}, status=403)
        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class TalentPortfolioAPIView(GenericAPIView):
    serializer_class = TalentPortfolioReadSerializer

    def get(self, request, public_id: str, *args, **kwargs):
        try:
            portfolio = (
                Talent.objects.get(public_id=public_id)
                .portfolio.filter()
                .order_by("-updated_at")
            )
            serializer = self.get_serializer(portfolio, many=True)
            return Response(serializer.data, status=200)
        except Talent.DoesNotExist:
            return Response({"message": "This request is prohibited"}, status=403)

        except Exception:

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

    def put(self, request, public_id: str, *args, **kwargs):
        try:
            pid = request.data.get("pid")
            portfolio = Portfolio.objects.get(id=pid, talent__user=request.user)
            serializer = self.get_serializer(instance=portfolio, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            raise Exception(str(serializer.errors))
        except Portfolio.DoesNotExist:
            return Response({"message": "This request is prohibited"}, status=403)
        except Exception as e:
            return Response({"message": str(e)}, status=400)

    def delete(self, request, public_id: str, *args, **kwargs):
        try:
            pid = request.data.get("pid")
            portfolio = Portfolio.objects.get(id=pid, talent__user=request.user)
            portfolio.delete()
            return Response({"message": "Portfolio deleted"}, status=200)
        except Portfolio.DoesNotExist:
            return Response({"message": "This request is prohibited"}, status=403)
        except:
            return Response({"message": "Bad request attempted"}, status=400)


class TalentDashboardStatsView(GenericAPIView):
    serializer_class = TalentDashboardSerializer

    def get(self, request, *args, **kwargs):
        profile, profile_type = request.user.profile
        if profile_type != "Talent":
            return Response({}, status=403)

        serializer = self.get_serializer(profile)
        return Response(serializer.data, status=200)
