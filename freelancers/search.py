from itertools import chain
from django.db.models import Q
from rest_framework.generics import ListAPIView
from .serializers import FreelancerSerializer
from utilities.text import get_url_search_params
from .models import Freelancer


from users.models import User


class FreelancersSearchAPIView(ListAPIView):
    permission_classes = []
    serializer_class = FreelancerSerializer

    @classmethod
    def make_query(cls, search_params: dict):
        category = search_params.get("category")
        location = search_params.get("location")
        badge = search_params.get("badge")
        rate = search_params.get("rate")
        query = search_params.get("query")

        queryset = Freelancer.objects.filter()

        if query:
            if query.lower() != "all":
                query = query.replace("%20", " ")
                queryset = queryset.filter(
                    Q(skills__icontains=query)
                    | Q(user__first_name__icontains=query)
                    | Q(user__last_name__icontains=query)
                    | Q(user__username__icontains=query)
                    | Q(title__icontains=query)
                    | Q(bio__icontains=query)
                    | Q(education__course__icontains=query)
                    | Q(education__description__icontains=query)
                )

        if category:
            if category.lower() != "all":
                category = category.replace("%20", " ")
                queryset = queryset.filter(
                    Q(skills__icontains=category)
                    | Q(title__icontains=category)
                    | Q(bio__icontains=category)
                    | Q(education__course__icontains=category)
                    | Q(education__description__icontains=category)
                )

        if badge:
            if badge.lower() != "all":
                badge = badge.replace("%20", " ")
                queryset = queryset.filter(Q(badge__icontains=badge))

        if location:
            if location.lower() != "all":
                queryset = queryset.filter(
                    Q(user__country__icontains=location)
                    | Q(user__state__icontains=location)
                    | Q(user__city__icontains=location)
                    | Q(user__address__icontains=location)
                    | Q(user__zip_code__icontains=location)
                )
        return queryset.order_by("badge").distinct()

    def get_queryset(self):
        return FreelancersSearchAPIView.make_query(self.request.query_params)  # type: ignore

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(page, many=True, context={"request": request})

        return self.get_paginated_response(serializer.data)
