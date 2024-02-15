from sre_parse import CATEGORIES
from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from datetime import datetime

from jobs.serializer import JobsSerializer

from utilities.text import get_url_search_params


from .models import Job


class JobsSearchAPIView(ListAPIView):
    permission_classes = []
    serializer_class = JobsSerializer

    def get_queryset(self):
        search_params = get_url_search_params(self.request.get_full_path())

        category = search_params.get("c")
        country = search_params.get("n")
        query = search_params.get("q")
        sort = search_params.get("s")

        queryset = Job.objects.filter()

        if query:
            query = query.replace("%20", " ")
            if query.lower() != "all":
                queryset = queryset.filter(
                    Q(category__startswith=query)
                    | Q(title__icontains=query)
                    | Q(description__icontains=query)
                    | Q(category__icontains=query)
                    | Q(required_skills__startswith=query)
                    | Q(required_skills__icontains=query)
                )

        if category:
            if category.lower() != "all":
                category = category.replace("%20", " ")
                queryset = queryset.filter(
                    Q(category__startswith=category)
                    | Q(category__icontains=category)
                    | Q(required_skills__startswith=category)
                    | Q(required_skills__icontains=category)
                )

        if sort:
            if sort.lower() != "all":
                sort = sort.replace("%20", " ")
                today = datetime.today()
                match sort.lower():
                    case "latest":
                        queryset = queryset.filter().order_by("-updated_at")
                    case "oldest":
                        queryset = queryset.filter().order_by("updated_at")
                    case "this_month":
                        queryset = queryset.filter(Q(updated_at__month=today.month) | Q(updated_at__month=today.month - 1)).order_by("updated_at")  # type: ignore
                        pass
                    case "last_month":
                        queryset = queryset.filter(Q(updated_at__month=today.month - 1) | Q(updated_at__month=today.month - 2)).order_by("updated_at")  # type: ignore
                        pass
                    case "recommended":
                        queryset.filter(active_state=True)

        if country:
            if country.lower() != "all":
                country = country.replace("%20", " ")
                queryset = queryset.filter(
                    Q(location__icontains=country)
                    | Q(location__startswith=country)
                    | Q(client__country__icontains=country)
                    | Q(client__country=country)
                )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(page, many=True, context={"request": request})

        return self.get_paginated_response(serializer.data)
