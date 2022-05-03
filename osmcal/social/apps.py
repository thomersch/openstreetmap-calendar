from django.apps import AppConfig
from django.db.models.signals import post_save


class SocialConfig(AppConfig):
    name = 'osmcal.social'

    def ready(self):
        from .post import announce_event
        post_save.connect(announce_event, sender='osmcal.Event')
