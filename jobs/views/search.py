import math
import re
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from datetime import datetime

from freelancers.models import Freelancer
from jobs.serializers import JobListSerializer

from jobs.models import Job


class JobsSearchAPIView(ListAPIView):
    permission_classes = []
    serializer_class = JobListSerializer

    def get_queryset(self):
        search_params = self.request.query_params  # type: ignore

        query = search_params.get("query")
        skills = search_params.get("skills")
        category = search_params.get("category")
        location = search_params.get("location")
        duration = search_params.get("duration")
        budget_rate = search_params.get("budget")
        order_by = search_params.get("order", "-created_at")

        if self.request.user.is_authenticated:

            self.queryset = Job.objects.filter(
                Q(is_valid=True, status="PUBLISHED") | Q(client__user=self.request.user)
            )
        else:
            self.queryset = Job.objects.filter(Q(is_valid=True, status="PUBLISHED"))

        if duration:
            self.filter_by_duration(duration)
        if category:
            self.filter_by_category(category)
        if location:
            self.filter_by_location(location)
        if skills:
            self.filter_by_skills(skills)
        if query:
            self.filter_by_query(query)
        if budget_rate:
            self.filter_by_budget(budget_rate)
        if order_by:
            if order_by == "relevance":
                self.get_relevance()
            elif order_by == "newest":
                self.queryset = self.queryset.order_by("created_at")
            elif order_by == "oldest":
                self.queryset = self.queryset.order_by("-created_at")
        else:
            self.queryset = self.queryset.order_by("-created_at")

        return self.queryset

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
        except Exception as e:
            return Response({"message": str(e)}, status=400)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={"request": request})

        return self.get_paginated_response(serializer.data)

    # Filters queryset by skills
    def filter_by_skills(self, skills: str):
        skills_filters = Q(required_skills__icontains=skills)
        self.queryset = self.queryset.filter(skills_filters)

    # Filters queryset by query
    def filter_by_query(self, query: str):
        query_filters = (
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(required_skills__icontains=query)
            | Q(location__icontains=query)
            | Q(category_obj__name__icontains=query)
            | Q(category_obj__slug__icontains=query)
        )
        self.queryset = self.queryset.filter(query_filters)

    # Filters queryset by location
    def filter_by_location(self, country: str):
        country = country.lower()

        qs = self.queryset.filter(location__icontains=country)

        if not qs.exists():
            first_3 = country[:3]
            the_rest = country[3:]

            sub_query_filters = Q(location__icontains=first_3)
            if the_rest:
                sub_query_filters |= Q(location__icontains=the_rest)

            qs = self.queryset.filter(sub_query_filters)
        self.queryset = qs

    # Filters queryset by category
    def filter_by_category(self, category: str):
        category_filters = Q(category_obj__slug__icontains=category) | Q(
            category_obj__name__icontains=category
        )
        qs = self.queryset.filter(category_filters)

        if not qs.exists():
            first_4 = category[:4]
            second_4 = category[4:8]
            third_4 = category[8:12]
            fourth_4 = category[12:16]

            sub_query_filters = Q(category_obj__slug=first_4) | Q(
                category_obj__name=first_4
            )

            for i in [second_4, third_4, fourth_4]:
                if not i:
                    continue
                sub_query_filters |= Q(category_obj__slug__icontains=i) | Q(
                    category_obj__name__icontains=i
                )
            qs = self.queryset.filter(sub_query_filters)
        self.queryset = qs

    # Filters queryset by most relevance
    def get_relevance(self):

        profile, profile_name = self.request.user.profile  # type: ignore
        freelancer: Freelancer | None = None

        if profile_name.lower() == "freelancer":
            freelancer = profile

        if freelancer:
            skills = freelancer.skills.split(",")
            filters = (
                Q(bits_count__gt=0)
                | Q(created_at__year=datetime.now().year)
                | Q(required_skills__in=skills)
                | Q(required_skills__iendswith=freelancer.skills)
                | Q(required_skills__istartswith=freelancer.skills)
                | Q(required_skills__icontains=freelancer.skills)
            )

            qs = self.queryset.filter(filters)
            if qs.exists():
                self.queryset = qs

    # Filters queryset by budget rate
    def filter_by_budget(self, budget: str):

        min_value = 0
        max_value = math.inf
        filters: Q | None = None

        try:

            if "-" in budget:
                min_budget, max_budget = budget.split("-")

                if max_budget.endswith("k"):
                    max_budget = int(max_budget[:-1]) * 1000
                else:
                    max_budget = int(max_budget)

                if min_budget.endswith("k"):
                    min_budget = int(min_budget[:-1]) * 1000
                else:
                    min_budget = int(min_budget)

                min_value = min_budget
                max_value = max_budget

            else:
                digits_before_k = re.findall(r"\d+", budget)
                min_value = int(digits_before_k[0]) * 1000

            if not min_value < 0:
                filters = Q(budget__gte=float(min_value))
            if filters and max_value != math.inf:
                filters &= Q(budget__lte=float(max_value))

        except Exception as e:
            pass

        if filters:
            self.queryset = self.queryset.filter(filters)

    # Filters queryset by duration
    def filter_by_duration(self, duration: str):
        qs = self.queryset.filter(duration__icontains=duration.strip())
        if qs.exists():
            # Apply the filters only if there is at least one result
            self.queryset = qs
