from datetime import datetime

from django.db.models import Avg, Count, F, Q, Sum
from rest_framework import serializers

from contracts.models import Contract
from talents.models import Certificate, Education, Portfolio, Talent
from users.serializer import User, UserSerializer


class TalentMiniSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = Talent
        fields = []

    def to_representation(self, instance: Talent):
        return {
            "username": instance.user.username,
            "avatar": instance.user.avatar,
            "name": instance.user.name,
            "rating": instance.user.calculate_rating(),
        }


class TalentSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = Talent
        fields = ("bio", "badge", "skills", "title", "pricing")

    def to_representation(self, instance: Talent):
        data = super().to_representation(instance)
        user: dict = UserSerializer(instance=instance.user).data  # type: ignore

        return {
            **user,
            **data,
            "rating": instance.user.calculate_rating(),
            "location": instance.user.get_location(),
        }


class TalentUpdateDataSerializer(serializers.ModelSerializer):
    """
    A readonly serializer for retrieving the updatable data of a talent
    """

    class Meta:
        model = Talent
        fields = []

    def to_representation(self, instance: Talent):
        return {
            **instance.user.get_personal_info(),
            # Address Info
            **instance.user.get_address(),
            # Client Info
            "bio": instance.bio,
            "email": instance.user.email,
            "pricing": instance.pricing,
            "skills": instance.skills,
            # User Info
            "name": instance.user.name,
            "avatar": instance.user.avatar,
            "gender": instance.user.gender,
            "username": instance.user.username,
            "first_name": instance.user.first_name,
            "last_name": instance.user.last_name,
            "date_joined": instance.user.date_joined,
        }


class TalentUpdateSerializer(serializers.ModelSerializer):
    """
    This serializer is used for the talent update view
    Exposes the talent's updatable fields
    """

    class Meta:
        model = Talent
        fields = (
            "title",
            "bio",
            "skills",
            "pricing",
        )

    @classmethod
    def merge_serialize(cls, instance, validated_data, **kwargs):
        data = dict()
        for field in cls.Meta.fields:
            if field in validated_data:
                data[field] = validated_data[field]
            else:
                data[field] = getattr(instance, field)
        return cls(instance=instance, data=data, **kwargs)


class TalentMiniInfoSerializer(serializers.ModelSerializer):
    """
    An Serializer for the talent information
    """

    class Meta:
        model = Talent
        fields = ("id", "bits", "pricing", "skills")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["pricing"] = float(data["pricing"])
        data["location"] = instance.user.get_location()
        data["skills"] = data.get("skills", "").split(", ")
        return data


class TalentDetailSerializer(serializers.ModelSerializer):
    """
    An API View for the talent data statistics
    """

    class Meta:
        model = Talent
        fields = ("bio", "badge", "pricing")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user: dict = UserSerializer(instance=instance.user).data  # type: ignore

        return {**user, **data}


class TalentProfileDetailSerializer(serializers.ModelSerializer):
    """
    An serializer class for the talent profile page
    """

    class Meta:
        model = Talent
        fields = [
            "bio",
            "title",
            "badge",
            "skills",
            "pricing",
            "jobs_completed",
        ]

    def to_representation(self, instance: Talent):
        data = super().to_representation(instance)
        user: dict = UserSerializer(instance=instance.user).data  # type: ignore
        data.update(user)
        data.update({"rating": instance.user.calculate_rating()})
        data.update({"address": instance.user.get_address()})
        return data


class TalentPortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = "__all__"

    def is_valid(self, *, raise_exception=False):
        self.initial_data = {
            "url": self.initial_data.get("url"),
            "name": self.initial_data.get("name"),
            "image": self.initial_data.get("image"),
            "description": self.initial_data.get("description"),
        }
        return super().is_valid(raise_exception=raise_exception)


# ===================== Certificate Serializers ===================== #
class TalentCertificateSerializer(serializers.ModelSerializer):
    id = serializers.CharField(required=False, read_only=True)
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)
    name = serializers.CharField(required=False)
    organization = serializers.CharField(required=False)
    url = serializers.URLField(required=False)
    published = serializers.BooleanField(required=False)
    date_issued = serializers.DateField(required=False)

    class Meta:
        model = Certificate
        fields = "__all__"


# ===================== Education Serializers ====================== #
class TalentEducationSerializer(serializers.ModelSerializer):
    id = serializers.CharField(required=False, read_only=True)
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)
    degree = serializers.CharField(required=False)
    institution = serializers.CharField(required=False)
    location = serializers.CharField(required=False)
    achievements = serializers.CharField(required=False, max_length=500)
    end_date = serializers.DateField(required=False)
    published = serializers.BooleanField(required=False)

    start_date = serializers.DateField(required=False)

    class Meta:
        model = Education
        fields = "__all__"


class TalentPortfolioCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ("image", "title", "description", "url")


class TalentDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Talent
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
                .filter(_query, talent=instance)
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

    def get_total_earning(self, instance: Talent):
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

        except Exception:
            pass
            return {"spent": 0.00}

    def get_client_reviews(self, instance: Talent):
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
        except Exception:
            pass
            return []

    def get_completed_projects(self, instance: Talent):
        completed_contracts = (
            self.projects.annotate(
                count=Count(F("completed_at__month")),
                year=F("completed_at__year"),
                month=F("completed_at__month"),
            )
            .values("budget", "month", "count", "year")
            .filter(job__completed=True)
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

    def get_profile_completion(self, instance: Talent):
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
                if portfolio != 1
                else "Done"
            ),
            "proposals": (
                "Make proposals to jobs interest you and stand a chance"
                if proposals != 1
                else "Done"
            ),
            "education": (
                "Include your education background details, this works for must talents"
                if education != 1
                else "Done"
            ),
            "biography": (
                "Your bio is one the the first thing client see on your profile, so enhancing it will help"
                if biography != 1
                else "Done"
            ),
            "email_address": (
                "Verify your email address to be able to use Dokoola witt ease. CRITICAL"
                if biography != 1
                else "Done"
            ),
        }

    def to_representation(self, instance: Talent):
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
