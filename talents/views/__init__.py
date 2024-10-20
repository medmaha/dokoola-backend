from rest_framework.generics import RetrieveAPIView, ListAPIView, GenericAPIView
from rest_framework.response import Response

from users.serializer import UserUpdateSerializer
from proposals.serializers import ProposalPendingListSerializer
from proposals.models import Proposal

from ..search import TalentsSearchAPIView

from ..serializers import (
    TalentDetailSerializer,
    TalentSerializer,
    TalentMiniInfoSerializer,
    TalentUpdateSerializer,
    TalentUpdateDataSerializer,
)

from ..dashboard import TalentDashboardSerializer

from ..models import Talent

from .portfolio import TalentPortfolioAPIView
from .certificates import TalentCertificateAPIView
from .education import TalentEducationAPIView


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

    def get(self, request, username, **kwargs):
        self.serializer_class = TalentUpdateDataSerializer
        try:
            talent = Talent.objects.get(user__username=username)
            talent_serializer: TalentUpdateDataSerializer = self.get_serializer(
                instance=talent, context={"request": request}
            )

            return Response(talent_serializer.data, status=200)
        except Talent.DoesNotExist:
            return Response(
                {"message": "Error: User doesn't exist!"},
                status=404,
            )

    def put(self, request, username, **kwargs):
        try:
            talent = Talent.objects.get(user__username=username)
            talent_serializer = TalentUpdateSerializer.merge_serialize(
                talent, request.data, context={"request": request}
            )
            if not talent_serializer.is_valid():
                # raised the same error as the serializer
                return Response(str(talent_serializer.errors), status=400)

            if not talent_serializer.is_valid():
                # raised the same error as the serializer
                return Response(str(talent_serializer.errors), status=400)

            user_serializer = UserUpdateSerializer.merge_serialize(
                talent.user, request.data, context={"request": request}
            )

            if not user_serializer.is_valid():
                # raised the same error as the serializer
                return Response(str(talent_serializer.errors), status=400)

            user_serializer.save()
            talent_serializer.save()

            return Response(talent_serializer.data, status=200)
        except Talent.DoesNotExist:
            return Response(
                {"message": "Error: User doesn't exist!"},
                status=404,
            )
        except Exception as e:

            return Response(
                {"message": "Error: Something went wrong!"},
                status=500,
            )


class FreelanceMiniInfoView(RetrieveAPIView):
    permission_classes = []
    serializer_class = TalentMiniInfoSerializer

    def retrieve(self, request, username, **kwargs):
        talent = Talent.objects.filter(user__username=username).first()

        if not talent:
            return Response({"message": "This request is prohibited"}, status=403)

        serializer = self.get_serializer(talent)

        return Response(serializer.data, status=200)


class TalentetrieveAPIView(RetrieveAPIView):
    serializer_class = TalentDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        username = self.kwargs.get("username")
        talent = (
            Talent.objects.prefetch_related("user")
            .filter(user__username=username)
            .first()
        )

        if not talent:
            return Response({"message": "This request is prohibited"}, status=403)

        serializer = self.get_serializer(talent)

        return Response(serializer.data, status=200)


class TalentProjectsList(ListAPIView):
    serializer_class = ProposalPendingListSerializer

    def get_queryset(self, username: str):
        try:
            talent = Talent.objects.select_related().get(user__username=username)
        except Talent.DoesNotExist:
            return None
        proposals = Proposal.objects.filter(job__is_valid=True, talent=talent)
        return proposals

    def list(self, request, username, *args, **kwargs):
        queryset = self.get_queryset(username)
        if not queryset:
            return Response({"message": "This request is prohibited"}, status=403)
        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class TalentDashboardStatsView(GenericAPIView):
    serializer_class = TalentDashboardSerializer

    def get(self, request, *args, **kwargs):
        profile, profile_type = request.user.profile
        if not profile_type == "Talent":
            return Response({}, status=403)

        serializer = self.get_serializer(profile)
        return Response(serializer.data, status=200)
