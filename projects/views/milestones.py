from django.db.models import Q
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.response import Response

from projects.models import Milestone, Project
from projects.serializers.milestone import (
    MilestoneCreateSerializer,
    MilestoneRetrieveSerializer,
    MilestoneUpdateSerializer,
)
from utilities.generator import get_serializer_error_message


class MilestoneCreateAPIView(CreateAPIView):
    serializer_class = MilestoneCreateSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        if not user.is_talent:
            return Response(
                {"message": "Only talents can create milestones"},
                status=400,
            )
        try:
            project = Project.objects.get(
                public_id=request.data.get("project_id", 0),
                contract__talent__user=user,
            )
        except:
            return Response({"message": "Project does not exist"}, status=400)

        data = request.data.copy()

        if data.get("published") in ["true", True]:
            data["published"] = True
        else:
            data["published"] = False

        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            milestone = serializer.save(project_pk=project.public_id)
            project.milestones.add(milestone)
            return Response(
                {
                    "message": "Milestone created successfully",
                },
                status=201,
            )

        error_message = get_serializer_error_message(serializer.errors)
        return Response({"message": error_message}, status=400)


class MilestoneUpdateAPIView(UpdateAPIView):
    serializer_class = MilestoneUpdateSerializer

    def update(self, request, *args, **kwargs):

        user = request.user

        if not user.is_talent:
            return Response(
                {"message": "Only talents can create milestones"},
                status=400,
            )
        try:
            project_id = request.data.get("project_id", 0)
            project = Project.objects.get(
                public_id=project_id,
                contract__talent__user=user,
            )
        except:
            return Response({"message": "Project does not exist"}, status=400)
        try:
            instance = Milestone.objects.get(
                id=request.data.get("milestone_id", 0),
                project_pk=project.public_id,
            )
        except:
            return Response({"message": "Milestone does not exist"}, status=400)

        data = request.data.copy()

        if data.get("published") in ["true", True]:
            data["published"] = True
        else:
            data["published"] = False

        serializer = self.get_serializer(instance, data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Milestone updated successfully",
                },
                status=200,
            )

        error_message = get_serializer_error_message(serializer.errors)
        return Response({"message": error_message}, status=400)


class MilestoneListAPIView(ListAPIView):
    serializer_class = MilestoneRetrieveSerializer

    def list(self, request, project_id: str, *args, **kwargs):

        user = request.user

        try:
            project = Project.objects.get(
                Q(public_id=project_id, contract__client__user=user)
                | Q(public_id=project_id, contract__talent__user=user)
            )
        except:
            return Response({"message": "Project does not exist"}, status=400)

        project.milestones

        milestones = Milestone.objects.filter(
            Q(
                published=True,
                project_pk=project.public_id,
                milestone_project__contract__client__user=user,
            )
            | Q(
                project_pk=project.public_id,
                milestone_project__contract__talent__user=user,
            ),
        )

        serializer = self.get_serializer(milestones, many=True)

        return Response(serializer.data)
