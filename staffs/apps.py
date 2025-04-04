from django.apps import AppConfig


class StaffsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "staffs"

    def ready(self) -> None:
        from . import signals

        return super().ready()
