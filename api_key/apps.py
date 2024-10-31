from django.apps import AppConfig


class ApiKeyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api_key'
    def ready(self):
        import api_key.signals 