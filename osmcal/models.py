from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db.models import PointField
from django.db import models

from enum import Enum

import requests


class EventType(Enum):
    SOCI = "Social"
    MEET = "Meeting"
    WORK = "Work"
    MAPE = "Map Event"
    CONF = "Conference"


class Event(models.Model):
    name = models.CharField(max_length=200)

    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)
    whole_day = models.BooleanField(default=False)

    location = PointField(blank=True, null=True)
    location_text = models.CharField(max_length=80, blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    kind = models.CharField(max_length=4, choices=[(x.name, x.value) for x in EventType])
    description = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        if not self.location_text and self.location:
            self.geocode_location()
        super().save(*args, **kwargs)

    def geocode_location(self):
        nr = requests.get('https://nominatim.openstreetmap.org/reverse', params={'format': 'jsonv2', 'lat': self.location.y, 'lon': self.location.x})
        addr = nr.json()['address']
        print(addr)
        self.location_text = ", ".join(filter(lambda x: x is not None, [addr.get('village'), addr.get('city'), addr.get('state'), addr.get('country_code').upper()]))

    class Meta:
        indexes = (
            models.Index(fields=('end',)),
        )


class User(AbstractUser):
    osm_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = 'osm_' + str(self.osm_id)
        super().save(*args, **kwargs)
