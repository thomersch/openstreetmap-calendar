from django.http import HttpResponse
from django.utils import timezone
from osmcal import views

from . import serializers
from .decorators import cors_any


class EventList(views.EventListView):
    @cors_any
    def get(self, request, *args, **kwargs):
        es = serializers.EventsSerializer(self.get_queryset(request.GET), context={'request': request})
        return HttpResponse(es.json, content_type='application/json')


class PastEventList(EventList):
    RESULT_LIMIT = 20

    def filter_queryset(self, qs, **kwargs):
        return qs.filter(start__lte=timezone.now()).order_by('-start')

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs)[:self.RESULT_LIMIT]
