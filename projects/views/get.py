from django.db.models import Q
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView

from projects.models.project import Project
from projects.serializers import ProjectListSerializer, ProjectRetrieveSerializer
from users.models.user import User


class ProjectListAPIView(ListAPIView):

    serializer_class = ProjectListSerializer

    def get_queryset(self, user: User):
        try:
            projects = Project.objects.filter(
                Q(contract__client__user=user) | Q(contract__talent__user=user)
            )
            return projects
        except:
            return None

    def list(self, request, *args, **kwargs):

        user: User = request.user
        queryset = self.get_queryset(user)

        if queryset is None:
            return Response({"message": "Resources not found"}, status=404)

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={"request": request})

        return self.get_paginated_response(serializer.data)


class ProjectRetrieveAPIView(RetrieveAPIView):

    serializer_class = ProjectRetrieveSerializer

    def get_queryset(self, user: User, project_id: str):
        try:
            project = Project.objects.get(
                Q(contract__client__user=user) | Q(contract__talent__user=user),
                id=project_id,
            )
            return project

        except:
            return None

    def retrieve(self, request, project_id: str, *args, **kwargs):

        user: User = request.user
        queryset = self.get_queryset(user, project_id)

        if queryset is None:
            return Response({"message": "Project does not exists"}, status=404)

        serializer = self.get_serializer(queryset, context={"request": request})

        # queryset.status = "PENDING"
        # queryset.save()

        return Response(serializer.data, status=200)
