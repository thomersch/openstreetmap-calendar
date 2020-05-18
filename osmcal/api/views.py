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
    def filter_queryset(self, qs, **kwargs):
        return qs.filter(start__lte=timezone.now()).order_by('-start')
