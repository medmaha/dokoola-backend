from django.db.models import Q
from rest_framework.response import Response
from rest_framework.generics import UpdateAPIView

from projects.serializers import ProjectStatusUpdateSerializer
from projects.models import Project, ProjectStatusChoices

from utilities.generator import get_serializer_error_message


class ProjectStatusUpdateAPIView(UpdateAPIView):
    serializer_class = ProjectStatusUpdateSerializer

    def update(self, request, project_id: str, *args, **kwargs):

        user = request.user

        if not user.is_talent and not user.is_client:
            return Response(
                {
                    "message": "forbidden! You don't have permission to perform this action"
                },
                status=403,
            )
        try:
            project = Project.objects.get(
                Q(
                    id=project_id,
                    contract__client__user=user,
                )
                | Q(
                    id=project_id,
                    contract__talent__user=user,
                ),
            )
        except:
            return Response({"message": "Project does not exist"}, status=400)

        serializer = self.get_serializer(project, data=request.data)

        if serializer.is_valid():
            serializer.save(project_pk=project.pk)
            return Response(
                {
                    "message": f"Project status updated successfully",
                },
                status=200,
            )

        error_message = get_serializer_error_message(serializer.errors)
        return Response({"message": error_message}, status=400)
