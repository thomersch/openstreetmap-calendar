from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.views import View
from osmcal import views
from pytz import timezone as tzp
from timezonefinder import TimezoneFinder

from . import serializers
from .decorators import ALLOWED_HEADERS, cors_any, language_from_header

JSON_CONTENT_TYPE = 'application/json; charset=' + settings.DEFAULT_CHARSET  # This shall be utf-8, otherwise we're not friends anymore.

tf = TimezoneFinder()


class CORSOptionsMixin(object):
    def options(self, request, *args, **kwargs):
        r = HttpResponse()
        r['Access-Control-Allow-Headers'] = ", ".join(ALLOWED_HEADERS)
        r['Access-Control-Allow-Origin'] = '*'
        return r


class EventList(CORSOptionsMixin, views.EventListView):
    def get_serializer(self):
        return serializers.EventsSerializer

    @cors_any
    @language_from_header
    def get(self, request, *args, **kwargs):
        es = self.get_serializer()(self.get_queryset(request.GET), context={'request': request})
        return HttpResponse(es.json, content_type=JSON_CONTENT_TYPE)


class PastEventList(EventList):
    RESULT_LIMIT = 20

    def filter_queryset(self, qs, **kwargs):
        return qs.filter(start__lte=timezone.now()).order_by('-local_start')

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs)[:self.RESULT_LIMIT]


class Timezone(View):
    def get(self, request, *args, **kwargs):
        lat = float(request.GET['lat'])
        lon = float(request.GET['lon'])
        tz = tf.timezone_at(lng=lon, lat=lat)
        if tz is None:
            return HttpResponse("", status=400)
        return HttpResponse(tzp(tz))
