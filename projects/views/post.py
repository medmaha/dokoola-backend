from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from projects.models import Project


from projects.serializers import ProjectCreateSerializer


class ProjectCreateAPIView(CreateAPIView):
    serializer_class = ProjectCreateSerializer
    queryset = Project.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)
