from datetime import datetime

from django.db.models import Avg, Sum, Count, F, Q
from rest_framework import serializers
from core.middleware.logger import DokoolaLogger
from freelancers.models import Freelancer
from jobs.models import Job
from users.models import User
from users.serializer import UserSerializer

from .models import Client, Review


class ClientSerializer(serializers.ModelSerializer):
    """
    A serializer for the client list api view
    Use to get the list of clients without much extra information
    """

    user = UserSerializer()

    class Meta:
        model = Client
        fields = ("id", "bio", "jobs_completed", "user")

    def to_representation(self, instance: Client):
        # TODO: return all necessary fields
        representation = super().to_representation(instance)
        representation["date_joined"] = instance.user.date_joined

        try:
            user_data = representation.pop("user")
            representation = {**user_data, **representation}
        except KeyError:
            pass
        return representation


class ClientUpdateDataSerializer(serializers.ModelSerializer):
    """
    A readonly serializer for retrieving the updatable data of a client

    """

    class Meta:
        model = Client
        fields = []

    def to_representation(self, instance: Client):
        return {
            # Client Info
            "bio": instance.bio,
            "phone": instance.phone,
            # Address Info
            **instance.get_address(),
            # User Info
            "email": instance.user.email,
            "name": instance.user.name,
            "avatar": instance.user.avatar,
            "gender": instance.user.gender,
            "username": instance.user.username,
            "first_name": instance.user.first_name,
            "last_name": instance.user.last_name,
            "date_joined": instance.user.date_joined,
        }


class ClientUpdateSerializer(serializers.ModelSerializer):
    """
    This serializer is used for the client update view
    Expose the client's updatable fields
    """

    class Meta:
        model = Client
        fields = (
            "bio",
            "phone",
            "phone_code",
            # Country Info
            "country",
            "country_code",
            "state",
            "district",
            "city",
            "zip_code",
            # Company Info
            "website",
            "industry",
        )


class ClientDetailSerializer(serializers.ModelSerializer):
    """
    A serializer for the client detail api view \n
    Securely serialize all the necessary information of this client
    * The return data will vary depending on the requesting user
    """

    user = UserSerializer()

    class Meta:
        model = Client
        fields = ("bio", "country", "address", "jobs_completed", "user")
        read_only_fields = ["*"]

    def to_representation(self, instance: Client):
        representation = super().to_representation(instance)
        representation["date_joined"] = instance.user.date_joined
        try:
            user_data = representation.pop("user")
            representation = {
                **user_data,
                **representation,
            }
        except KeyError:
            pass
        return representation


class ClientProfileDetailSerializer(serializers.ModelSerializer):
    """
    A serializer for the client detail api view \n
    Securely serialize all the necessary information of this client
    * The return data will vary depending on the requesting user
    """

    class Meta:
        model = Client
        fields = [
            "bio",
            "website",
            "industry",
            "jobs_active",
            "jobs_created",
            "jobs_completed",
        ]

    def get_address(self, instance: Client):
        request = self.context.get("request")
        user = request.user if request else None
        if user and user.pk == instance.user.pk:
            return instance.get_address()
        return instance.address

    def to_representation(self, instance: Client):
        data = super().to_representation(instance)
        user: dict = UserSerializer(instance=instance.user).data  # type: ignore
        data.update(user)
        data.update({"rating": instance.calculate_rating()})
        data.update({"address": self.get_address(instance)})
        data.update({"reviews": []})
        return data


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "rating", "content")

    def to_representation(self, instance: Review):
        data = super().to_representation(instance)
        data["author"] = (
            {
                "username": instance.author.username,
                "avatar": instance.author.avatar,
                "name": instance.author.name,
            }
            if instance.author
            else None
        )


class ClientJobDetailSerializer(serializers.ModelSerializer):
    """
    This serializer is used for the job detail view
    * The return data will vary depending on the requesting user
    """

    class Meta:
        model = Client
        fields = (
            "bio",
            "rating",
            "reviews",
            "country",
            "address",
            "jobs_active",
            "jobs_created",
            "jobs_completed",
        )

    # Gets the client's basic user information and returns it
    def user_info(self, user: User):
        return {
            "avatar": user.avatar,
            "name": user.name,
            "username": user.username,
        }

    # Calculate how much this client has been spent on jobs
    def calculate_spent(self, instance: Client):
        # get the all jobs created by this client
        completed_jobs = Job.objects.select_related().filter(
            client=instance, completed=True
        )
        return completed_jobs.aggregate(Sum("budget"))["budget__sum"] or 0

    def to_representation(self, instance: Client):

        representation = super().to_representation(instance)
        representation["rating"] = instance.calculate_rating()
        representation["date_joined"] = instance.user.date_joined
        representation["total_spent"] = self.calculate_spent(instance)
        representation.update(self.user_info(instance.user))

        return representation


class ClientDashboardStatsSerializer(serializers.ModelSerializer):
    """
    A serializer for the client dashboard statistics view
    """

    def __init__(self, instance=None, *args, **kwargs):
        super().__init__(instance, *args, **kwargs)  # type: ignore
        kwargs.setdefault("extra", {"query": {}})

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
            self.projects = Job.objects.select_related().filter(_query, client=instance)

    def get_months(self, x):
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
        ][x]

    def get_total_projects(self, instance: Client):
        try:
            total = self.projects.count()
            last_month = self.projects.filter(
                created_at__month=self._last_month
            ).count()
            this_month = self.projects.filter(
                created_at__month=self._this_month
            ).count()
            percentage = ((this_month / 100) / (last_month / 100)) * 100

            if (percentage) > 100:
                percentage = 100
            return {
                "total": total,
                "this_month": this_month,
                "last_month": last_month,
                "percentage": int(percentage),
            }
        except Exception as e:
            message = f"{e} - [FILE:clients.serializer.py BLOCK:ClientDashboardStatsSerializer.get_total_projects]"
            DokoolaLogger.critical(message)
            return {"total": 0.00}

    def get_total_spending(self, instance: Client):
        try:
            spent = self.projects.aggregate(Sum("budget"))["budget__sum"] or 0.00
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
            percentage = ((this_month / 100) / (last_month / 100)) * 100

            if (percentage) > 100:
                percentage = 100

            return {
                "spent": spent,
                "this_month": this_month,
                "last_month": last_month,
                "percentage": int(percentage),
            }
        except Exception as e:
            message = f"{e} - [FILE:clients.serializer.py BLOCK:ClientDashboardStatsSerializer.get_total_spending]"
            DokoolaLogger.critical(message)
            return {"spent": 0.00}

    def get_average_rating(self, instance: Client):
        try:
            average = instance.reviews.select_related()
            this_month = average.filter(created_at__month=self._this_month)
            last_month = average.filter(created_at__month=self._last_month)

            data = {
                "count": average.count(),
                "average": average.aggregate(Avg("rating"))["rating__avg"] or 0.01,
                "this_month": this_month.aggregate(Avg("rating"))["rating__avg"]
                or 0.01,
                "last_month": last_month.aggregate(Avg("rating"))["rating__avg"]
                or 0.01,
            }
            data["percentage"] = (
                (data["this_month"] / 100) / (data["last_month"] / 100)
            ) * 100

            if (data["percentage"]) > 100:
                data["percentage"] = 100
        except Exception as e:
            message = f"{e} - [FILE:clients.serializer.py BLOCK:ClientDashboardStatsSerializer.get_average_rating]"
            DokoolaLogger.critical(message)

        return data

    def get_project_types(self, instance: Client):
        try:
            projects = (
                self.projects.order_by("-created_at")
                # .distinct("category")
                .values("slug").annotate(
                    label=F("category"),
                    year=F("created_at__year"),
                    month=F("created_at__month"),
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
                    "month": self.get_months(project["month"]),
                    "label": project["label"],
                    "count": self.projects.filter(category=project["label"])
                    .values()
                    .count(),
                }
                for project in projects
            ]
        except Exception as e:
            message = f"{e} - [FILE:clients.serializer.py BLOCK:ClientDashboardStatsSerializer.get_project_types]"
            DokoolaLogger.critical(message)

    def get_project_spending(self, instance: Client):

        try:
            projects = self.projects.values("id", "budget", "category").annotate(
                year=F("created_at__year"),
                month=F("created_at__month"),
            )

            result = []

            for category in projects:
                months = projects.filter(created_at__month=category["month"]).annotate(
                    spent=Sum("budget"),
                    month=F("created_at__month"),
                    year=F("created_at__year"),
                )
                unique = {}

                for m in months:
                    unique[m["category"]] = m

                result.append(
                    {
                        "id": category["id"],
                        "name": category["month"],
                        "year": category["year"],
                        "data": [
                            {
                                "year": month["year"],
                                "label": self.get_months(month["month"] - 1),
                                "category": month["category"],
                                "x": self.get_months(month["month"] - 1),
                                "y": projects.filter(
                                    created_at__month=month["month"],
                                )
                                .aggregate(budget=Sum("budget"))
                                .get("budget"),
                            }
                            for month in list(unique.values())[:6]
                        ],
                    }
                )
            return result
        except Exception as e:
            message = f"{e} - [FILE:clients.serializer.py BLOCK:ClientDashboardStatsSerializer.get_project_spending]"
            DokoolaLogger.critical(message)
            return []

    def get_freelancer_reviews(self, instance: Client):
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
            message = f"{e} - [FILE:clients.serializer.py BLOCK:ClientDashboardStatsSerializer.get_freelancer_reviews]"
            DokoolaLogger.critical(message)
            return []

    def get_recent_projects(self, instance: Client):
        projects = self.projects.values(
            "slug",
            "title",
            "description",
            "status",
            "category",
            "budget",
            "created_at",
        )[:5]

        computed = []
        try:
            for i, project in enumerate(projects[:5]):

                freelancers = Freelancer.objects.select_related("user").filter(
                    contract__job=project
                )
                computed.append(project)
                if freelancers.exists():
                    _freelancer = freelancers[0]

                    data = {}
                    data["freelancer"] = {
                        "name": _freelancer.user.name,
                        "title": _freelancer.title,
                        "avatar": _freelancer.user.avatar,
                        "username": _freelancer.user.username,
                        **_freelancer.reviews.select_related().aggregate(
                            rating=Avg("rating", 3)
                        ),
                    }

                    computed[i] = data
            raise ValueError("Column does not exists")
        except Exception as e:
            message = f"{e} - [FILE:clients.serializer.py BLOCK:ClientDashboardStatsSerializer.get_recent_projects]"
            DokoolaLogger.critical(message)
        return computed

    def to_representation(self, instance: Client):
        representation = super().to_representation(instance)

        representation["project_types"] = self.get_project_types(instance)
        representation["total_spending"] = self.get_total_spending(instance)
        representation["total_projects"] = self.get_total_projects(instance)
        representation["project_spending"] = self.get_project_spending(instance)
        representation["freelancer_reviews"] = self.get_freelancer_reviews(instance)
        representation["recent_projects"] = self.get_recent_projects(instance)
        representation["avg_rating"] = self.get_average_rating(instance)

        return representation

    class Meta:
        model = Client
        fields = (
            "rating",
            "reviews",
            "country",
            "jobs_active",
            "jobs_created",
            "jobs_completed",
        )
