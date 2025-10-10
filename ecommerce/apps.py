from django.apps import AppConfig


class EcommerceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ecommerce"

    def ready(self):
        # Import signal handlers to connect them with Django's signal framework
        # noqa: F401 (imported for side effects)
        import ecommerce.signals  # noqa: F401
