from django.http import HttpResponse
from osmcal import views

from . import serializers


class EventList(views.EventListView):
    def get(self, request, *args, **kwargs):
        es = serializers.EventsSerializer(self.get_queryset(request.GET), context={'request': request})
        return HttpResponse(es.json, content_type='application/json', charset='utf-8')
