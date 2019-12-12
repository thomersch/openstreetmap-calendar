import json

from django.template.loader import render_to_string
from django.urls import reverse


class BaseSerializerMany(object):
    def __init__(self, objs, context={}):
        self.objs = objs
        self.context = context

    @property
    def json(self):
        out = []

        for obj in self.objs:
            oo = {}
            for field in self.fields:
                try:
                    oo[field] = getattr(self, "attr_" + field)(obj)
                except AttributeError:
                    oo[field] = getattr(obj, field)
            out.append(oo)

        return json.dumps(out, ensure_ascii=False)


class EventsSerializer(BaseSerializerMany):
    fields = ('name', 'url', 'date', 'location')

    def attr_date(self, obj):
        o = {
            'human': render_to_string('osmcal/date.txt', {'event': obj}).strip(),
            'whole_day': obj.whole_day,
            'start': str(obj.start),
        }
        if obj.end:
            o['end'] = str(obj.end)
        return o

    def attr_location(self, obj):
        o = {
            'short': obj.location_text,
            'detailed': obj.location_detailed_addr
        }
        return o

    def attr_url(self, obj):
        rel_url = reverse('event', args=[obj.id])
        try:
            return self.context['request'].build_absolute_uri(rel_url)
        except KeyError:
            return rel_url
