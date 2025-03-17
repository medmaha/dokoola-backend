from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.response import Response

from ..models import Talent
from ..search import TalentsSearchAPIView
from ..serializers import (
    TalentRetrieveSerializer,
    TalentMiniInfoSerializer,
    TalentSerializer,
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


class TalentMiniInfoView(RetrieveAPIView):
    permission_classes = []
    serializer_class = TalentMiniInfoSerializer

    def retrieve(self, request, public_id, **kwargs):
        talent = Talent.objects.filter(public_id=public_id).first()

        if not talent:
            return Response({"message": "This request is prohibited"}, status=403)

        serializer = self.get_serializer(talent)

        return Response(serializer.data, status=200)


class TalentRetrieveAPIView(RetrieveAPIView):
    serializer_class = TalentRetrieveSerializer

    def retrieve(self, request, public_id, **kwargs):
        talent = (
            Talent.objects.prefetch_related("user")
            .filter(public_id=public_id)
            .first()
        )

        if not talent:
            return Response({"message": "This request is prohibited"}, status=403)

        serializer = self.get_serializer(talent)
        return Response(serializer.data, status=200)
