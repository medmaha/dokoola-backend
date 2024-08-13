from django.apps import AppConfig


class ContractsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "contracts"

    def ready(self) -> None:
        from contracts import signals

        return super().ready()
