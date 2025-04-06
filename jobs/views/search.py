import math
from random import shuffle
import re
from datetime import datetime

from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from jobs.models import Job
from jobs.models.job import JobStatusChoices, JobTypeChoices
from jobs.serializers import JobListSerializer
from talents.models import Talent
from users.models.user import User


active_statues = [
    JobStatusChoices.PUBLISHED,
    # JobStatusChoices.SUSPENDED,
    # JobStatusChoices.CLOSED,
    # JobStatusChoices.DELETED
    # JobStatusChoices.CONTRACTED
]

guest_job_query = Q(is_valid=True, status__in=active_statues)
client_job_query = lambda user_id: Q(
    client__user__pk=user_id,
    status__in=[
        *active_statues,
        JobStatusChoices.CLOSED,
        JobStatusChoices.PENDING,
        JobStatusChoices.CONTRACTED,
        JobStatusChoices.COMPLETED,
        JobStatusChoices.IN_PROGRESS,
    ],
)


def user_query(user: User|None, queryset):
    profile, profile_type = user.profile if user else (None, "")
    if user and user.is_authenticated:
        queryset = queryset.filter(guest_job_query & Q(published=True) | client_job_query(user.pk))
    else:
        queryset = Job.objects.filter(
            guest_job_query,
            published=True,
        )

    if profile and profile_type == "Talent":
        queryset = queryset.exclude(public_id__in=profile.applications_ids)

    return queryset


class JobsSearchAPIView(ListAPIView):
    permission_classes = []
    serializer_class = JobListSerializer

    def get_queryset(self, user:User|None):
        search_params = self.request.query_params  # type: ignore

        query = search_params.get("query")
        skills = search_params.get("skills")
        category = search_params.get("category")
        address = search_params.get("location")
        duration = search_params.get("duration")
        budget_rate = search_params.get("budget")
        order_by = search_params.get("order", "-created_at")
        job_type = search_params.get("type")

        self.queryset = Job.objects.filter()

        if duration:
            self.filter_by_duration(duration)
        if category:
            self.filter_by_category(category)
        if address:
            self.filter_by_address(address)
        if skills:
            self.filter_by_skills(skills)
        if job_type:
            self.filter_by_job_type(job_type)
        if query:
            self.filter_by_query(query)
        if order_by:
            if order_by == "relevance":
                self.get_relevance()
            elif order_by == "newest":
                self.queryset = self.queryset.order_by("created_at")
            elif order_by == "oldest":
                self.queryset = self.queryset.order_by("-created_at")
        else:
            self.queryset = self.queryset.order_by("-created_at")

        queryset = user_query(user, self.queryset)

        if not queryset and category:
            queryset = Job.objects.filter(
                Q(title__icontains=category) |
                Q(description__icontains=category) |
                Q(required_skills__icontains=category) |
                Q(third_party_metadata___short_description__icontains=category)
            )
            queryset = user_query(user, queryset)

        # if not queryset:
        #     queryset = user_query(user, Job.objects.filter()).order_by("public_id")[:10]
        #     shuffle(list(queryset))

        return queryset.distinct()

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset(request.user)
        except Exception as e:
            return Response({"message": str(e)}, status=400)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)

    # Filters queryset by skills
    def filter_by_job_type(self, _job_type: str):
        job_type = str(_job_type).lower()
        value = None
        if "full" in job_type:
            value = JobTypeChoices.FULL_TIME.value.lower()
        if job_type == JobTypeChoices.FULL_TIME.value.lower():
            value = job_type
        if "part" in job_type:
            value = JobTypeChoices.PART_TIME.value.lower()
        if job_type == JobTypeChoices.PART_TIME.value.lower():
            value = job_type
        if job_type == JobTypeChoices.CONTRACT.value.lower():
            value = job_type
        if job_type == JobTypeChoices.INTERNSHIP.value.lower():
            value = job_type
        if job_type == JobTypeChoices.FREELANCE.value.lower():
            value = job_type
        if job_type == JobTypeChoices.OTHER.value.lower():
            value = job_type
        if _job_type and isinstance(_job_type, str):
            value = _job_type.lower()
        if not value:
            return
        
        self.queryset = self.queryset.filter(job_type__icontains=value)

    def filter_by_skills(self, skills: str):
        skills_filters = Q(required_skills__icontains=skills)
        self.queryset = self.queryset.filter(skills_filters)

    # Filters queryset by query
    def filter_by_query(self, query: str):
        query_filters = (
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(required_skills__icontains=query)
            | Q(address__icontains=query)
            | Q(country__name__icontains=query)
            | Q(category__name__icontains=query)
            | Q(category__slug__icontains=query)
        )
        self.queryset = self.queryset.filter(query_filters)

    # Filters queryset by address
    def filter_by_address(self, location: str):
        location = location.lower()

        qs = self.queryset.filter(Q(address__icontains=location) | Q(country__name__icontains=location))

        if not qs.exists():
            first_3 = location[:3]
            the_rest = location[3:]

            sub_query_filters = Q(address__icontains=first_3)
            if the_rest:
                sub_query_filters |= Q(address__icontains=the_rest)

            qs = self.queryset.filter(sub_query_filters)
        self.queryset = qs

    # Filters queryset by category
    def filter_by_category(self, category: str):
        category_filters = Q(category__slug__icontains=category) | Q(
            category__name__icontains=category
        )
        qs = self.queryset.filter(category_filters)

        if not qs.exists():
            first_4 = category[:4]
            second_4 = category[4:8]
            third_4 = category[8:12]
            fourth_4 = category[12:16]

            sub_query_filters = Q(category__slug=first_4) | Q(category__name=first_4)

            for i in [second_4, third_4, fourth_4]:
                if not i:
                    continue
                sub_query_filters |= Q(category__slug__icontains=i) | Q(
                    category__name__icontains=i
                )
            qs = self.queryset.filter(sub_query_filters)
        self.queryset = qs

    # Filters queryset by most relevance
    def get_relevance(self):

        profile, profile_name = self.request.user.profile  # type: ignore
        talent: Talent | None = None

        if profile_name.lower() == "talent":
            talent = profile

        if talent:
            skills = talent.skills.split(",")
            filters = (
                Q(bits_count__gt=0)
                | Q(created_at__year=datetime.now().year)
                | Q(required_skills__in=skills)
                | Q(required_skills__iendswith=talent.skills)
                | Q(required_skills__istartswith=talent.skills)
                | Q(required_skills__icontains=talent.skills)
            )

            qs = self.queryset.filter(filters)
            if qs.exists():
                self.queryset = qs

    # Filters queryset by duration
    def filter_by_duration(self, duration: str):
        qs = self.queryset.filter(application_duration__icontains=duration.strip())
        if qs.exists():
            # Apply the filters only if there is at least one result
            self.queryset = qs
