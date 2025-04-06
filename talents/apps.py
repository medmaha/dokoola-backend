from django.apps import AppConfig


class TalentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "talents"

    def ready(self) -> None:
        from . import signals
        return super().ready()
