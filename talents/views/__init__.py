from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
)
from rest_framework.response import Response

from proposals.models import Proposal
from proposals.serializers import ProposalPendingListSerializer

from ..dashboard import TalentDashboardSerializer
from ..models import Talent
from ..search import TalentsSearchAPIView
from .certificates import TalentCertificateAPIView
from .education import TalentEducationAPIView
from .portfolio import TalentPortfolioAPIView

from .get import TalentListAPIView, TalentRetrieveAPIView, TalentMiniInfoView
from .put import (
    TalentUpdateAPIView,
)


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


class TalentDashboardStatsView(GenericAPIView):
    serializer_class = TalentDashboardSerializer

    def get(self, request, *args, **kwargs):
        profile, profile_type = request.user.profile
        if profile_type != "Talent":
            return Response({}, status=403)

        serializer = self.get_serializer(profile)
        return Response(serializer.data, status=200)


__all__ = [
    "TalentDashboardStatsView",
    "TalentProjectsList",
    "TalentCertificateAPIView",
    "TalentEducationAPIView",
    "TalentPortfolioAPIView",
    "TalentListAPIView",
    "TalentRetrieveAPIView",
    "TalentMiniInfoView",
    "TalentUpdateAPIView",
    "TalentsSearchAPIView",
]
