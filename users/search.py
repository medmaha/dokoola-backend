from django.db.models import F, Q
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from clients.models import Client  # client_profile
from talents.models import Talent  # talents_profile

from .models import User


class UserProfileAPIQueryView(GenericAPIView):
    permission_classes = []

    def get_talent_queries(self, query: str):
        return (
            Q(talent_profile__title__icontains=query)
            | Q(talent_profile__bio__icontains=query)
            | Q(talent_profile__skills__icontains=query)
        )

    def get_client_queries(self, query: str):

        return Q(client_profile__bio__icontains=query)

    def get_user_queries(self, query: str):

        return Q(first_name__icontains=query) | Q(last_name__icontains=query)

    def get_queryset(self, query: str, model: str):

        queries = self.get_user_queries(query)
        if model.lower() in "talents":
            queries = queries | self.get_talent_queries(query)
        elif model.lower() in "clients":
            queries = queries | self.get_client_queries(query)

        talents = (
            User.objects.select_related()
            .filter(queries)
            .exclude(Q(is_superuser=True) | Q(is_staff=True) | Q(is_active=False))
            .order_by("-last_login")
            .values("first_name", "last_name", "avatar", "username")
        )

        return talents

    def get(self, request, *args, **kwargs):

        query = request.query_params.get("q")
        model = request.query_params.get("m")

        if not query:
            return Response([], status=200)

        queryset = self.get_queryset(query, model)

        page = self.paginate_queryset(queryset)

        if page is not None:
            return self.get_paginated_response(page)

        return Response(queryset, status=200)
