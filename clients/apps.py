from django.apps import AppConfig


class AppsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "clients"

    def ready(self) -> None:
        from . import signals
        return super().ready()
