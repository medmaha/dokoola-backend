from django.db import models
from rest_framework import serializers
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from clients.models import Client
from projects.models.project import Project, ProjectStatusChoices
from users.models import User
from utilities.formatters import get_month_index, get_month_name


class ClientDashboardSerializer(serializers.Serializer):

    pass


class ClientDashboardAPIView(RetrieveAPIView):
    """
    This view is used for the client dashboard view
    Retrieves all information/statistics related to the client
    """

    permission_classes = []

    def get_queryset(self, user: User, query_params: dict):

        client = Client.objects.get(user=user)

        year = None
        if "year" in query_params:
            year = int(query_params["year"])

        month = None
        if "month" in query_params:
            month = int(query_params["month"])

        query = ClientDashboardQuery(client, month=month, year=year)

        data = {}
        data["project_types"] = query.get_project_types()
        data["total_spending"] = query.total_spending()
        data["total_projects"] = query.get_total_projects()
        data["project_spending"] = query.get_project_spending()
        data["talent_reviews"] = query.get_talent_reviews()
        data["recent_projects"] = query.get_recent_projects()
        data["avg_rating"] = query.get_average_rating()

        return data

    def retrieve(self, request, *args, **kwargs):
        try:
            dashboard_data = self.get_queryset(request.user, request.query_params)
            return Response(dashboard_data, status=200)
        except (ValueError, TypeError) as e:
            message = e.__str__()
            return Response({"message": message}, status=404)

        except Exception as e:
            message = "An error occurred while processing your request"
            return Response({"message": message}, status=500)


class ClientDashboardQuery:

    def __init__(
        self,
        instance: Client,
        month: int | None = None,
        year: int | None = None,
    ):

        from datetime import datetime

        from proposals.models import Job

        self.today = datetime.now()
        self.year: int | None = None
        self.month = self.today.month

        if month and isinstance(month, int):
            self.month = get_month_index(get_month_name(month))
        if year and isinstance(year, int):
            self.year = year

        self.instance = instance

        self.__projects = (
            Project.objects.select_related()
            .filter(
                contract__client=self.instance,
            )
            .annotate(
                budget=models.F("contract__proposal__budget"),
            )
        )

        project_ids = self.__projects.values_list("id", flat=True)

        self.__jobs = Job.objects.select_related().filter(
            proposals__contract__project__id__in=project_ids,
            client=self.instance,
        )

    def total_spending(self):

        try:
            projects_budgets = self.__projects

            accepted_projects = (
                projects_budgets.filter(status=ProjectStatusChoices.ACCEPTED).aggregate(
                    models.Sum("budget")
                )["budget__sum"]
                or 0.00
            )

            pending_projects = (
                projects_budgets.filter(
                    status__in=[
                        ProjectStatusChoices.PENDING,
                        ProjectStatusChoices.COMPLETED,
                    ]
                ).aggregate(models.Sum("budget"))["budget__sum"]
                or 0.00
            )

            spent = accepted_projects
            pending_spent = pending_projects

            last_month = (
                projects_budgets.filter(
                    created_at__month=(self.month - 1) or 1
                ).aggregate(models.Sum("budget"))["budget__sum"]
            ) or 0.01

            this_month = (
                projects_budgets.filter(created_at__month=self.month).aggregate(
                    models.Sum("budget")
                )["budget__sum"]
            ) or 0.00

            percentage = (float(this_month / 100) / float(last_month / 100)) * 100

            if (percentage) > 100:
                percentage = 100

            return {
                "spent": spent,
                "this_month": this_month,
                "last_month": last_month,
                "percentage": int(percentage),
                "pending_spent": pending_spent,
            }
        except Exception:
            return {"spent": 0.00}

    def get_total_projects(self):
        try:
            total = self.__projects.count()
            last_month = self.__projects.filter(
                created_at__month=(self.month - 1) or 1
            ).count()
            this_month = self.__projects.filter(created_at__month=self.month).count()
            percentage = (
                float(this_month or 0.01 / 100) / float(last_month or 0.01 / 100)
            ) * 100

            if (percentage) > 100:
                percentage = 100

            return {
                "total": total,
                "this_month": this_month,
                "last_month": last_month,
                "percentage": int(percentage),
            }
        except Exception:
            return {"total": 0.00}

    def get_project_spending(self):

        try:

            # Annotate custom fields with month, year and category
            projects = self.__projects.values("id", "budget").annotate(
                category=models.F("contract__job__category_obj__name"),
                year=models.F("created_at__year"),
                month=models.F("created_at__month"),
            )

            result = []

            for category in projects:

                # Groups all projects by category and month
                months = projects.filter(created_at__month=category["month"]).annotate(
                    spent=models.Sum("budget"),
                    month=models.F("created_at__month"),
                    year=models.F("created_at__year"),
                )

                unique = {}

                # Loop through months
                for single_month in months:

                    unique[single_month["category"]] = single_month

                result.append(
                    {
                        "id": category["id"],
                        "name": category["month"],
                        "year": category["year"],
                        "data": [
                            {
                                "year": month["year"],
                                "label": get_month_name(month["month"]),
                                "category": month["category"],
                                "x": get_month_name(month["month"]),
                                "y": projects.filter(
                                    created_at__month=month["month"],
                                )
                                .aggregate(budget=models.Sum("budget"))
                                .get("budget"),
                            }
                            for month in list(unique.values())[:6]
                        ],
                    }
                )
            return result
        except Exception:

            # DokoolaLogger.critical(message)

            return []

    def get_average_rating(self):
        reviews = self.instance.reviews.select_related()

        this_month = reviews.filter(created_at__month=(self.month - 1) or 1)
        last_month = reviews.filter(created_at__month=self.month)

        data = {
            "count": reviews.count(),
            "average": reviews.aggregate(models.Avg("rating"))["rating__avg"] or 0.01,
            "this_month": this_month.aggregate(models.Avg("rating"))["rating__avg"]
            or 0.01,
            "last_month": last_month.aggregate(models.Avg("rating"))["rating__avg"]
            or 0.01,
        }
        data["percentage"] = (
            (data["this_month"] / 100) / (data["last_month"] / 100)
        ) * 100

        if (data["percentage"]) > 100:
            data["percentage"] = 100

        return data

    def get_project_types(self):
        projects = (
            self.__jobs.order_by("-created_at")
            # .distinct("category")
            .values("slug").annotate(
                label=models.F("category_obj__name"),
                year=models.F("created_at__year"),
                month=models.F("created_at__month"),
            )
        )

        _projects = {}

        for p in projects:
            _projects[p["label"]] = p

        projects = list(_projects.values())[:6]

        return [
            {
                "id": project["slug"],
                "year": project["year"],
                "month": get_month_name(project["month"]),
                "label": project["label"],
                "count": self.__jobs.filter(category_obj__name=project["label"])
                .values()
                .count(),
            }
            for project in projects
        ]

    def get_recent_projects(self):
        from talents.models import Talent

        # projects = self.__jobs.values(
        #     "slug",
        #     "title",
        #     "description",
        #     "status",
        #     "budget",
        #     "created_at",
        # ).annotate(category=models.F("category_obj__name"))[:5]

        computed = []

        return computed

    def get_talent_reviews(self):
        try:
            _query = models.Q(pk__isnull=False)

            ratings = (
                self.instance.reviews.select_related()
                .filter(_query)
                .values("id")
                .annotate(
                    year=models.F("created_at__year"),
                    month=models.F("created_at__month"),
                )
            )

            duplicate = {}
            for review in ratings:
                duplicate[review["month"]] = review

            result = [
                {
                    "id": rating["id"],
                    "year": rating["year"],
                    "month": get_month_name(rating["month"]),
                    **self.instance.reviews.select_related()
                    .filter(_query, created_at__month=rating["month"])
                    .aggregate(
                        count=models.Count("id", 0),
                        avg_rating=models.Avg("rating", 0, distinct=True),
                    ),
                }
                for rating in list(duplicate.values())[:6]
            ]
            return result
        except Exception:

            return []
