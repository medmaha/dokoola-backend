import uuid

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from core.services.logger.main import DokoolaLoggerService
from jobs.models.job import Job, JobStatusChoices
from src.features.paginator import DokoolaPaginator
from users.models.user import User
from users.serializer import UserUpdateSerializer
from utilities.generator import get_serializer_error_message

from .models import Client, Company
from .serializer import (
    ClientCreateSerializer,
    ClientJobDetailSerializer,
    ClientJobPostingSerializer,
    ClientListSerializer,
    ClientRetrieveSerializer,
    ClientUpdateDataSerializer,
    ClientUpdateSerializer,
    CompanyCreateSerializer,
    CompanyUpdateSerializer,
)


def validate_uuid(_id):
    try:
        uuid.UUID(_id)
        return True
    except ValueError:
        return False


class ClientGenericAPIView(GenericAPIView):
    """
    A generic api view for performing CRUD operations on clients
    """

    permission_classes = []

    def get_queryset(self):
        queryset = Client.objects.all()
        return queryset

    def get(self, request, client_id=None, *args, **kwargs):

        try:

            if client_id:
                queryset = Client.objects.get(
                    Q(public_id=client_id) | Q(user__username=client_id)
                )
                serializer = ClientRetrieveSerializer(
                    queryset, context={"request": request}
                )

            else:
                queryset = self.get_queryset()
                page = self.paginate_queryset(queryset)

                # Check if paginator is enabled
                if page is not None:
                    serializer = ClientListSerializer(
                        page, many=True, context={"request": request}
                    )
                    return self.get_paginated_response(serializer.data)

                serializer = ClientListSerializer(
                    queryset, many=True, context={"request": request}
                )
            return Response(serializer.data, status=200)

        except:
            return Response(
                {"message": "The provided query, doesn't match our database"},
                status=400,
            )

    def post(self, request):

        data = request.data.copy()
        user = data.pop("user", None)
        company = data.pop("company", None)

        if not user:
            return Response({"message": "User is required"}, status=400)

        try:
            with transaction.atomic():
                _client = Client(**data)
                _client.full_clean(["user", "company"])

                password = user.get("password", None)
                if not password:
                    return Response(
                        {"message": "User password is required"},
                        status=400,
                    )

                _user = User(**user)
                _user.is_client = True
                _user.full_clean()
                _user.set_password(password)

                if company:
                    _company = Company(**company)
                    _company.clean()
                else:
                    _company = None

                serializer = ClientCreateSerializer(data=request.data)

                if serializer.is_valid():
                    _user.save()
                    if _company:
                        _company.save()
                    client = serializer.save(company=_company, user=_user)
                    response_serializer = ClientListSerializer(instance=client)
                    return Response(response_serializer.data, status=201)

                error_message = get_serializer_error_message(
                    serializer.errors, "This is a bad ass request"
                )
                return Response({"message": str(error_message)}, status=400)
        except Exception as e:
            return Response({"message": str(e)}, status=500)

    def put(self, request, client_id, *args, **kwargs):
        try:
            data = request.data.copy()
            user_data = data.pop("user", None)
            company_data = data.pop("company", None)

            user: User = request.user

            if not user.is_client:
                msg = "Forbidden! only clients are allowed"
                DokoolaLoggerService.lazy.warning(
                    msg,
                    extra={
                        "type": "handler_error",
                        "response.status": 403,
                        "session.id": str(request.session),
                        "error.message": msg,
                        "client.public_id": client_id,
                        "request.user_id": request.user.pk,
                        "request.handler": self.__name__,
                        "request.user_data": user_data,
                        "request.company_data": company_data,
                    },
                )
                return Response(
                    {"message": msg},
                    status=403,
                )

            _client = None
            _serializers = []

            _valid_uuid = validate_uuid(client_id)

            with transaction.atomic():
                if _valid_uuid:
                    _client = Client.objects.get(public_id=client_id)
                else:
                    _client = Client.objects.get(user__username=client_id)

                assert user.pk == _client.user.pk, "Forbidden request"

                if company_data:

                    if not _client.company:
                        _serializers.append(CompanyCreateSerializer(data=data))
                    else:
                        _serializers.append(
                            CompanyUpdateSerializer.merge_serialize(
                                _client.company, company_data
                            )
                        )
                if user_data:
                    _serializers.append(
                        UserUpdateSerializer.merge_serialize(user, user_data)
                    )

                _serializers.append(
                    ClientUpdateSerializer.merge_serialize(_client, data)
                )

                for serializer in _serializers:
                    if not serializer.is_valid():
                        error_message = get_serializer_error_message(
                            serializer.errors, "This is a bad ass request"
                        )
                        DokoolaLoggerService.lazy.warning(
                            "Invalid updata-data passed",
                            extra={
                                "type": "handler_error",
                                "response.status": 400,
                                "session.id": str(request.session),
                                "error.message": "Invalid updata-data passed",
                                "client.public_id": client_id,
                                "request.user_id": request.user.pk,
                                "serializer": serializer.__name__,
                                "error.type": "serializer.ValidationError",
                                "request.handler": self.__name__,
                                "request.data": serializer.initial_data,
                            },
                        )
                        return Response({"message": str(error_message)}, status=400)

                    obj = serializer.save()

                    # Set the client's company
                    if isinstance(obj, Company) and not _client.company:
                        _client.company = obj
                        _client.save()

                if _valid_uuid:
                    _client = Client.objects.get(pk=client_id)
                else:
                    _client = Client.objects.get(user__username=client_id)

                response_serializer = ClientListSerializer(instance=_client)
                return Response(response_serializer.data, status=200)

        except Client.DoesNotExist:
            DokoolaLoggerService.lazy.warning(
                "Invalid request parameters",
                extra={
                    "type": "handler_error",
                    "response.status": 400,
                    "session.id": str(request.session),
                    "error.message": "Invalid request parameters",
                    "client.public_id": client_id,
                    "request.user_id": request.user.pk,
                    "error.type": "Client.DoesNotExist",
                    "request.handler": self.__name__,
                },
            )
            return Response({"message": "Invalid request parameters"}, status=400)

        except AssertionError as e:
            msg = str(e)
            DokoolaLoggerService.lazy.error(
                msg,
                extra={
                    "type": "handler_error",
                    "response.status": 403,
                    "session.id": str(request.session),
                    "error.message": msg,
                    "client.public_id": client_id,
                    "request.user_id": request.user.pk,
                    "error.type": "AssertionError",
                    "request.handler": self.__name__,
                },
            )
            return Response({"message": str(e)}, status=403)

        except Exception as e:
            msg = str(e)
            DokoolaLoggerService.lazy.error(
                msg,
                extra={
                    "type": "handler_error",
                    "response.status": 500,
                    "session.id": str(request.session),
                    "error.message": msg,
                    "client.public_id": client_id,
                    "request.user_id": request.user.pk,
                    "error.type": "Exception",
                    "request.handler": self.__name__,
                },
            )
            return Response({"message": str(e)}, status=500)

    def delete(self, request, client_id, *args, **kwargs):
        try:
            user: User = request.user

            if not user.is_authenticated:
                return Response({"message": "Unauthenticated request"}, status=401)

            if not user.is_client:
                return Response(
                    {"message": "Forbidden! Only clients are allowed"},
                    status=403,
                )

            client = Client.objects.get(pk=client_id)

            assert user.pk == client.user.pk, "Forbidden request"

            client.deleted_at = timezone.now()

            if client.company:
                client.company.deleted_at = client.deleted_at
                client.company.save()

            client.save()

            user.is_active = False
            user.save()

            return Response(status=204)
        except Exception as e:
            error = str(e)
            return Response({"message": error}, status=404)


class UserAPIView(RetrieveAPIView):
    serializer_class = ClientListSerializer

    def get_queryset(self):
        user_id = self.kwargs["pk"]
        if not user_id:
            return None
        try:
            queryset = Client.objects.get(pk=user_id)
            return queryset
        except Client.DoesNotExist:
            return None

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            serializer = self.get_serializer(
                instance=queryset, context={"request": request}
            )
            return Response(serializer.data, status=200)
        return Response(
            {"message':'The userID provided, doesn't match our database"},
            status=404,
        )


class ClientUpdateView(GenericAPIView):
    """
    This view is used for the client mini api view
    Retrieves clients updatable information
    """

    permission_classes = []
    serializer_class = ClientUpdateDataSerializer

    def get(self, request, username, **kwargs):
        self.serializer_class = ClientUpdateDataSerializer
        try:
            client = Client.objects.get(user__username=username)
            client_serializer: ClientUpdateDataSerializer = self.get_serializer(
                instance=client, context={"request": request}
            )
            return Response(client_serializer.data, status=200)
        except Client.DoesNotExist:
            return Response(
                {"message": "Error: User doesn't exist!"},
                status=404,
            )

    def put(self, request, username, **kwargs):
        self.serializer_class = ClientUpdateSerializer
        try:
            client = Client.objects.get(user__username=username)
            client_serializer: ClientUpdateSerializer = self.get_serializer(
                instance=client,
                data=request.data,
                context={"request": request},
            )

            if not client_serializer.is_valid():
                # raised the same error as the serializer
                return Response(str(client_serializer.errors), status=400)
            client_serializer.save()
            return Response(client_serializer.data, status=200)
        except Client.DoesNotExist:
            return Response(
                {"message": "Error: User doesn't exist!"},
                status=404,
            )
        except Exception:

            return Response(
                {"message": "Error: Something went wrong!"},
                status=500,
            )


class ClientJobDetailView(RetrieveAPIView):
    """
    This view is used for the job detail view
    Retrieves all information related to the job about it's client
    """

    permission_classes = []
    serializer_class = ClientJobDetailSerializer

    def get_queryset(self, kwargs):

        username = kwargs.get("usr")
        job_slug = kwargs.get("slug")

        if not (username and job_slug):
            return None

        # job = Job.objects.get(slug=job_slug)
        job = None
        client = Client.objects.get(user__username=username)

        return client, job

    def retrieve(self, request, *args, **kwargs):
        try:
            client, job = self.get_queryset(request.query_params)  # type: ignore
            client_serializer = self.get_serializer(
                instance=client, context={"request": request}
            )
            return Response(client_serializer.data, status=200)
        except Exception:

            return Response(
                {"message": "The provided query, doesn't match our database"},
                status=404,
            )


class ClientRecentJobPaginator(DokoolaPaginator):
    page_size = 5


class ClientJobPostingApiView(ListAPIView):
    """
    This view is used for the job posting view.
    Gets the recent jobs created by the client
    """

    pagination_class = ClientRecentJobPaginator
    serializer_class = ClientJobPostingSerializer

    def list(self, request, username, *args, **kwargs):
        try:
            active_statues = [
                JobStatusChoices.PUBLISHED,
                JobStatusChoices.COMPLETED,
                JobStatusChoices.IN_PROGRESS,
                # JobStatusChoices.SUSPENDED,
                # JobStatusChoices.CLOSED,
                # JobStatusChoices.DELETED
            ]

            valid_job_query = Q(is_valid=True, status__in=active_statues)
            client_job_query = Q(
                client__user__username=username, status__in=active_statues
            )

            query = valid_job_query | client_job_query

            identity_query = Q(client__public_id=username) | Q(
                client__user__username=username
            )
            other_users_query = identity_query & Q(
                is_valid=True,
                published=True,
                status__in=[
                    JobStatusChoices.PUBLISHED,
                    JobStatusChoices.IN_PROGRESS,
                    JobStatusChoices.COMPLETED,
                ],
            )
            owner_query = identity_query & Q(
                is_valid=True,
                status__in=[
                    JobStatusChoices.PUBLISHED,
                    JobStatusChoices.IN_PROGRESS,
                    JobStatusChoices.COMPLETED,
                ],
            )

            jobs = Job.objects.filter(query).order_by("published", "-created_at")  # type: ignore

            page = self.paginate_queryset(jobs)
            serializer = self.get_serializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        except Exception as e:
            return Response(
                {"message": "The provided query, doesn't match our database"},
                status=404,
            )
