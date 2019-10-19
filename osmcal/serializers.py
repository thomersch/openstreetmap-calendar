from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.gis.geos.point import Point


class JSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Point):
            return obj.wkt
        return super().default(obj)
