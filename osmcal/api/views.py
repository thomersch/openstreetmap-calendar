from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from osmcal import views

from . import serializers
from .decorators import cors_any, language_from_header

JSON_CONTENT_TYPE = 'application/json; charset=' + settings.DEFAULT_CHARSET  # This shall be utf-8, otherwise we're not friends anymore.


class EventList(views.EventListView):
    @cors_any
    @language_from_header
    def get(self, request, *args, **kwargs):
        es = serializers.EventsSerializer(self.get_queryset(request.GET), context={'request': request})
        return HttpResponse(es.json, content_type=JSON_CONTENT_TYPE)


class PastEventList(EventList):
    RESULT_LIMIT = 20

    def filter_queryset(self, qs, **kwargs):
        return qs.filter(start__lte=timezone.now()).order_by('-start')

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs)[:self.RESULT_LIMIT]
