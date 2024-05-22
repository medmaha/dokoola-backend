from rest_framework.generics import ListAPIView, RetrieveAPIView, GenericAPIView
from rest_framework.response import Response

from jobs.models import Job
from .serializer import (
    ClientSerializer,
    ClientUpdateDataSerializer,
    ClientJobDetailSerializer,
    ClientUpdateSerializer,
)
from .models import Client


class ClientListView(ListAPIView):
    """
    Gets the list of all clients and returns a paginated response
    """

    permission_classes = []
    serializer_class = ClientSerializer

    def get_queryset(self):
        queryset = Client.objects.all()
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        # Check if paginator is enabled
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=200)


class UserAPIView(RetrieveAPIView):
    serializer_class = ClientSerializer

    def get_queryset(self):
        user_id = self.kwargs["pk"]
        if not user_id:
            return None
        try:
            queryset = Client.objects.get(pk=user_id)
            return queryset
        except:
            return None

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            serializer = self.get_serializer(
                instance=queryset, context={"request": request}
            )
            return Response(serializer.data, status=200)
        return Response(
            {"message':'The userID provided, doesn't match our database"}, status=404
        )


class ClientUpdateView(GenericAPIView):
    """
    This view is used for the client mini api view
    Retrieves clients updatable information
    """

    permission_classes = []

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
                instance=client, data=request.data, context={"request": request}
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
        except Exception as e:
            print("Exception:", e)
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
        except Exception as e:
            print("Exception:", e)
            return Response(
                {"message": "The provided query, doesn't match our database"},
                status=404,
            )
