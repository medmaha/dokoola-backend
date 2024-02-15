from django.apps import AppConfig


class FreelancersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "freelancers"
    
    def ready(self) -> None:
        from . import signals

        return super().ready()
