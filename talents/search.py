from django.db.models import Q
from rest_framework.generics import ListAPIView

from .models import Talent
from .serializers import TalentReadSerializer


class TalentsSearchAPIView(ListAPIView):
    permission_classes = []
    serializer_class = TalentReadSerializer

    @classmethod
    def make_query(cls, request):
        search_params = request.query_params
        category = search_params.get("category")
        location = search_params.get("location")
        badge = search_params.get("badge")
        rate = search_params.get("rate")
        query = search_params.get("query")

        queryset = Talent.objects.filter()

        if query and query.lower() != "all":
            query = query.replace("%20", " ")
            queryset = queryset.filter(
                Q(skills__icontains=query)
                | Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(user__public_id__icontains=query)
                | Q(title__icontains=query)
                | Q(bio__icontains=query)
                | Q(skills__icontains=query)
            )

        if category and category.lower() != "all":
            category = category.replace("%20", " ")
            queryset = queryset.filter(
                Q(skills__icontains=category)
                | Q(title__icontains=category)
                | Q(bio__icontains=category)
            )

        if badge and badge.lower() != "all":
            badge = badge.replace("%20", " ")
            queryset = queryset.filter(Q(badge__icontains=badge))

        if location and location.lower() != "all":
            queryset = queryset.filter(
                Q(user__country__icontains=location)
                | Q(user__state__icontains=location)
                | Q(user__city__icontains=location)
                | Q(user__address__icontains=location)
                | Q(user__zip_code__icontains=location)
            )
        return queryset.select_related("user")

    def get_queryset(self):
        return TalentsSearchAPIView.make_query(self.request.query_params)  # type: ignore

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(
            page, many=True, context={"request": request, "mini": True}
        )

        return self.get_paginated_response(serializer.data)
