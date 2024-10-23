from django.db import models


class Acknowledgement(models.Model):

    comment = models.TextField(null=True, blank=True)
    acknowledged = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_project(self):
        project = self.project  # type: ignore
        return project

    def get_milestone(self):
        milestone = self.project.milestone  # type: ignore
        return milestone
