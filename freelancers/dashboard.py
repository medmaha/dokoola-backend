from datetime import datetime
from django.db.models import Q, F, Sum, Avg, Count

from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import serializers

from jobs.models.job import JobStatusChoices
from contracts.models import Contract
from freelancers.models import Freelancer


class FreelancerDashboardQuery(GenericAPIView):
    permission_classes = []

    def get_queryset(self, query: str):

        freelancers = (
            Freelancer.objects.select_related()
            .filter(
                Q(title__icontains=query)
                | Q(bio__icontains=query)
                | Q(skills__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
            )
            .annotate(
                avatar=F("user__avatar"),
                username=F("user__username"),
                first_name=F("user__first_name"),
                last_name=F("user__last_name"),
            )
            .order_by("-user__last_login")
            .values("first_name", "last_name", "avatar", "username")
        )

        return freelancers

    def get(self, request, *args, **kwargs):

        query = request.query_params.get("q")

        if not query:
            return Response([], status=200)

        queryset = self.get_queryset(query)

        page = self.paginate_queryset(queryset)

        if page is not None:
            return self.get_paginated_response(page)

        return Response(queryset, status=200)


class FreelancerDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Freelancer
        fields = []

    def __init__(self, instance, *args, **kwargs) -> None:
        super().__init__(instance, *args, **kwargs)
        request = self.context.get("request")
        if request is not None:
            query_params: dict = request.query_params
        else:
            query_params = {}

        self.year = None
        self.today = datetime.today()
        self._last_month = (
            self.today.month - 1 if self.today.month > 1 else self.today.month
        )
        self._this_month = self.today.month

        if instance is not None:
            try:
                if query_params.get("year"):
                    self.year = int(query_params.get("year") or self.today.year)

            except:
                pass

            _query = Q(created_at__year=self.year) if self.year else Q(pk__isnull=False)

            self.projects = (
                Contract.objects.select_related()
                .annotate(budget=F("proposal__budget"))
                .filter(_query, freelancer=instance)
            )

    def get_months(self, index: int):
        return [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ][index]

    def get_total_earning(self, instance: Freelancer):
        try:
            earnings = self.projects.aggregate(Sum("budget"))["budget__sum"] or 0.00
            last_month = (
                self.projects.filter(created_at__month=self._last_month).aggregate(
                    Sum("budget")
                )["budget__sum"]
                or 0.00
            )
            this_month = (
                self.projects.filter(created_at__month=self._this_month).aggregate(
                    Sum("budget")
                )["budget__sum"]
                or 0.00
            )
            if this_month and last_month:
                percentage = ((this_month / 100) / (last_month / 100)) * 100
            else:
                percentage = 0

            return {
                "earned": earnings,
                "this_month": this_month,
                "last_month": last_month,
                "percentage": int(percentage),
            }

        except Exception as e:
            pass
            return {"spent": 0.00}

    def get_client_reviews(self, instance: Freelancer):
        try:
            _query = Q(created_at__year=self.year) if self.year else Q(pk__isnull=False)

            ratings = (
                instance.reviews.select_related()
                .filter(_query)
                .values("id")
                .annotate(
                    year=F("created_at__year"),
                    month=F("created_at__month"),
                )
            )

            duplicate = {}
            for review in ratings:
                duplicate[review["month"]] = review

            result = [
                {
                    "id": rating["id"],
                    "year": rating["year"],
                    "month": self.get_months(rating["month"] - 1),
                    **instance.reviews.select_related()
                    .filter(_query, created_at__month=rating["month"])
                    .aggregate(count=Count("id", 0), avg_rating=Avg("rating")),
                }
                for rating in list(duplicate.values())[:6]
            ]
            return result
        except Exception as e:
            pass
            return []

    def get_completed_projects(self, instance: Freelancer):
        completed_contracts = (
            self.projects.annotate(
                count=Count(F("completed_at__month")),
                year=F("completed_at__year"),
                month=F("completed_at__month"),
            )
            .values("budget", "month", "count", "year")
            .filter(job__status=JobStatusChoices.COMPLETED)
        )

        unique = {}
        computed = list(completed_contracts)[:6]

        for project in computed:

            project["month"] = self.get_months(project["month"] - 1)

            _id = project["month"]

            if unique.get(_id):
                unique[_id]["budget"] += project["budget"]
                unique[_id]["count"] += project["count"]
            else:
                unique[_id] = project

        if unique.keys():
            computed = list(unique.values())
        return computed

    def get_profile_completion(self, instance: Freelancer):
        portfolio = float(instance.portfolio.exists()) or 0.017
        proposals = float(instance.proposals.exists()) or 0.021  # type: ignore
        education = float(instance.education.exists()) or 0.016
        biography = 1 if len(instance.bio) else 0.02
        email_verified = int(instance.user.email_verified) or 0.01

        avg = ((email_verified + portfolio + proposals + education + biography) / 5) * (
            100
        )
        avg = float(str(avg)[:4])

        return {
            "percentage": avg,
            "portfolio": (
                "Add a portfolio or resume that proves your profession"
                if not 1 == portfolio
                else "Done"
            ),
            "proposals": (
                "Make proposals to jobs interest you and stand a chance"
                if not 1 == proposals
                else "Done"
            ),
            "education": (
                "Include your education background details, this works for must freelancers"
                if not 1 == education
                else "Done"
            ),
            "biography": (
                "Your bio is one the the first thing client see on your profile, so enhancing it will help"
                if not 1 == biography
                else "Done"
            ),
            "email_address": (
                "Verify your email address to be able to use Dokoola witt ease. CRITICAL"
                if not 1 == biography
                else "Done"
            ),
        }

    def to_representation(self, instance: Freelancer):
        # representation = super().to_representation(instance)
        super().to_representation(instance)
        data = {
            "username": instance.user.username,
            "rating": instance.user.calculate_rating(),
            "total_earning": self.get_total_earning(instance),
            "client_reviews": self.get_client_reviews(instance),
            "completed_projects": self.get_completed_projects(instance),
            "profile_completion": self.get_profile_completion(instance),
        }

        return data
