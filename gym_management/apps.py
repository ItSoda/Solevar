from django.apps import AppConfig


class GymManagementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "gym_management"

    def ready(self) -> None:
        from gym_management import signals
