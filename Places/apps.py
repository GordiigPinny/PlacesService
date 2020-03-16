from django.apps import AppConfig


class PlacesConfig(AppConfig):
    name = 'Places'

    def ready(self):
        from . import signals
