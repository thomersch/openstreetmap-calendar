import json

from django.template.loader import render_to_string
from django.urls import reverse


class Omitable(object):
    """
    This value is empty and the key should be omitted.
    If you're thinking: "What is that crazy german guy doing?", well the answer
    is simple: I didn't want to pull in the whole of rest framework and hacked
    some code. Now it escalated. If you wanna change all of that crap to DRF,
    feel free :)
    """


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
                    v = getattr(self, "attr_" + field)(obj)
                    if not isinstance(v, Omitable):
                        oo[field] = v
                except AttributeError:
                    oo[field] = getattr(obj, field)
            out.append(oo)

        return json.dumps(out, ensure_ascii=False)


class EventsSerializer(BaseSerializerMany):
    fields = ('name', 'url', 'date', 'location', 'cancelled')

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
        if not obj.location:
            return Omitable()

        o = {
            'short': obj.location_text,
            'detailed': obj.location_detailed_addr,
            'coords': [obj.location.x, obj.location.y]
        }

        if obj.location_name:
            o['venue'] = obj.location_name
        return o

    def attr_url(self, obj):
        rel_url = reverse('event', args=[obj.id])
        try:
            return self.context['request'].build_absolute_uri(rel_url)
        except KeyError:
            return rel_url

    def attr_cancelled(self, obj):
        if not obj.cancelled:
            return Omitable()
        return obj.cancelled
