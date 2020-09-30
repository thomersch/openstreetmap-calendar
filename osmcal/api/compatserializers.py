from django.template.loader import render_to_string

from .serializers import EventsSerializer

"""Serializers that are used by older versions of the API"""


class EventsV1Serializer(EventsSerializer):
    def attr_date(self, obj):
        o = {
            'human': render_to_string('osmcal/date.l10n.txt', {'event': obj}).strip(),
            'whole_day': obj.whole_day,
            'start': str(obj.start_localized.replace(tzinfo=None)),
        }
        if obj.end:
            o['end'] = str(obj.end_localized.replace(tzinfo=None))
        return o
