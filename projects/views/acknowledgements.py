from django.db.models import Q
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView

from projects.serializers import (
    AcknowledgementCreateSerializer,
    AcknowledgementUpdateSerializer,
    AcknowledgementRetrieveSerializer,
)
from projects.models import Project, Acknowledgement, ProjectStatusChoices

from utilities.generator import get_serializer_error_message


class AcknowledgementCreateAPIView(CreateAPIView):
    serializer_class = AcknowledgementCreateSerializer

    def create(self, request, *args, **kwargs):

        user = request.user

        if not user.is_client:
            return Response(
                {"message": "Only clients can create acknowledgements"}, status=400
            )
        try:
            project = Project.objects.get(
                id=request.data.get("project_id", 0), contract__client__user=user
            )

            if project.status not in [
                ProjectStatusChoices.COMPLETED,
                ProjectStatusChoices.CANCELLED,
                ProjectStatusChoices.ACCEPTED,
            ]:
                return Response(
                    {"message": "Project cannot be acknowledged at this point."},
                    status=403,
                )

        except:
            return Response({"message": "Project does not exist"}, status=400)

        data = request.data.copy()

        if data.get("acknowledged") in ["true", True]:
            data["acknowledged"] = True
        else:
            data["acknowledged"] = False

        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            acknowledgement = serializer.save()
            project.acknowledgement = acknowledgement
            project.save()
            return Response(
                {
                    "message": "Acknowledgement created successfully",
                },
                status=201,
            )

        error_message = get_serializer_error_message(serializer.errors)
        return Response({"message": error_message}, status=400)


class AcknowledgementUpdateAPIView(UpdateAPIView):
    serializer_class = AcknowledgementUpdateSerializer

    def update(self, request, *args, **kwargs):

        user = request.user

        if not user.is_client:
            return Response(
                {"message": "Only clients can create acknowledgements"}, status=400
            )
        try:
            project = Project.objects.get(
                id=request.data.get("project_id", 0), contract__client__user=user
            )
            if project.status not in [
                ProjectStatusChoices.COMPLETED,
                ProjectStatusChoices.CANCELLED,
                ProjectStatusChoices.ACCEPTED,
            ]:
                return Response(
                    {
                        "message": "Project Acknowledged cannot be updated at this point."
                    },
                    status=403,
                )
            instance = project.acknowledgement
        except:
            return Response({"message": "Project does not exist"}, status=400)

        data = request.data.copy()

        if data.get("acknowledged") in ["true", True]:
            data["acknowledged"] = True
        else:
            data["acknowledged"] = False

        serializer = self.get_serializer(instance=instance, data=data)

        if serializer.is_valid():
            serializer.save(project_pk=project.pk)
            return Response(
                {
                    "message": "Acknowledgement updated successfully",
                },
                status=200,
            )

        error_message = get_serializer_error_message(serializer.errors)
        return Response({"message": error_message}, status=400)


class AcknowledgementRetrieveAPIView(RetrieveAPIView):
    serializer_class = AcknowledgementRetrieveSerializer

    def retrieve(self, request, project_id: str, *args, **kwargs):

        user = request.user

        try:
            project = Project.objects.get(
                Q(id=project_id, contract__client__user=user)
                | Q(id=project_id, contract__talent__user=user),
            )
        except:
            return Response({"message": "Project does not exist"}, status=400)

        if project.acknowledgement:
            serializer = self.get_serializer(project.acknowledgement)
            return Response(serializer.data)
        return Response(None, status=200)
