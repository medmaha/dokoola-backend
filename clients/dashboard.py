from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView

from django.db import models

from clients.models import Client
from utilities.formatters import get_month_index, get_month_name
from users.models import User

from core.middleware.logger import DokoolaLogger


class ClientDashboardAPIView(RetrieveAPIView):
    """
    This view is used for the client dashboard view
    Retrieves all information/statistics related to the client
    """

    permission_classes = []

    def get_queryset(self, user: User, query_params:dict):

        client = Client.objects.get(user=user)

        year = None
        if "year" in query_params:
            try:
                year = int(query_params["year"])
            except:
                pass
        month = None
        if "month" in query_params:
            try:
                month = int(query_params["month"])
            except:
                pass

        query =  ClientDashboardQuery(client, month=month, year=year)

        data = {}
        data["project_types"] = query.get_project_types()
        data["total_spending"] =  query.total_spending()
        data["total_projects"] = query.get_total_projects()
        data["project_spending"] = query.get_project_spending()
        data["freelancer_reviews"] = query.get_freelancer_reviews()
        data["recent_projects"] = query.get_recent_projects()
        data["avg_rating"] = query.get_average_rating()
        
        return data

    def retrieve(self, request, *args, **kwargs):
        try:
            dashboard_data = self.get_queryset(request.user, request.query_params)  # type: ignore
            return Response(dashboard_data, status=200)
        except Exception as e:
            return Response(
                {"message": "The provided query, doesn't match our database"},
                status=404,
            )



class ClientDashboardQuery():

    def __init__(self, instance:Client, month:int|None=None, year:int|None=None):

        from datetime import datetime
        from proposals.models import Job

        self.today = datetime.now()
        self.year: int | None = None 
        self.month = self.today.month

        if month and isinstance(month, int):
            self.month = get_month_index(get_month_name(month)
                                    )
        if year and isinstance(year, int):
            self.year = year

        self.instance = instance
        self.__projects = Job.objects.select_related().filter(client=self.instance)
    

    def total_spending(self):
       
        try:
            spent = self.__projects.aggregate(models.Sum("budget"))["budget__sum"] or 0.00
            last_month = (
                self.__projects.filter(created_at__month=(self.month - 1) or 1).aggregate(
                    models.Sum("budget")
                )["budget__sum"]
               
            )  or 0.01
            this_month = (
                self.__projects.filter(created_at__month=self.month).aggregate(
                    models.Sum("budget")
                )["budget__sum"]
            )  or 0.00
            percentage = (float(this_month / 100) / float(last_month / 100)) * 100

            if (percentage) > 100:
                percentage = 100

            return {
                "spent": spent,
                "this_month": this_month,
                "last_month": last_month,
                "percentage": int(percentage),
            }
        except Exception as e:
            
            
            return {"spent": 0.00}


    def get_total_projects(self):
        try:
            total = self.__projects.count()
            last_month = self.__projects.filter(
                created_at__month=(self.month - 1) or 1
            ).count()
            this_month = self.__projects.filter(
                created_at__month=self.month
            ).count()
            percentage = (float(this_month or 0.01 / 100)  / float(last_month or 0.01 / 100)) * 100

            if (percentage) > 100:
                percentage = 100

            return {
                "total": total,
                "this_month": this_month,
                "last_month": last_month,
                "percentage": int(percentage),
            }
        except Exception as e:
            
            
            return {"total": 0.00}


    def get_project_spending(self):

        try:
            projects = self.__projects.values("id", "budget").annotate(
                category=models.F("category_obj__name"),
                year=models.F("created_at__year"),
                month=models.F("created_at__month"),
            )

            result = []

            for category in projects:
                months = projects.filter(created_at__month=category["month"]).annotate(
                    spent=models.Sum("budget"),
                    month=models.F("created_at__month"),
                    year=models.F("created_at__year"),
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
        except Exception as e:
            
            # DokoolaLogger.critical(message)
            

            return []


    def get_average_rating(self):
        try:
            reviews = self.instance.reviews.select_related()
            
            this_month = reviews.filter(created_at__month=(self.month -1) or 1)
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
        except Exception as e:
            pass
            

        return data
    

    def get_project_types(self):
        try:
            projects = (
                self.__projects.order_by("-created_at")
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
                    "count": self.__projects.filter(category_obj__name=project["label"])
                    .values()
                    .count(),
                }
                for project in projects
            ]
        except Exception as e:
            pass
            


    def get_recent_projects(self):
        from freelancers.models import Freelancer

        projects = self.__projects.values(
            "slug",
            "title",
            "description",
            "status",
            "budget",
            "created_at",
        ).annotate(category=models.F("category_obj__name"))[:5]

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
                            rating=models.Avg("rating", 3)
                        ),
                    }

                    computed[i] = data
        except Exception as e:
            pass
            
        return computed


    def get_freelancer_reviews(self):
        try:
            _query =  models.Q(pk__isnull=False)

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
                    .aggregate(count=models.Count("id", 0), avg_rating=models.Avg("rating", 0, distinct=True)),
                }
                for rating in list(duplicate.values())[:6]
            ]
            return result
        except Exception as e:
            
            
            return []
