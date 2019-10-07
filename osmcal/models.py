from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db.models import PointField
from django.contrib.postgres.fields.jsonb import JSONField
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
    location_address = JSONField(blank=True, null=True)

    link = models.URLField(blank=True, null=True)
    kind = models.CharField(max_length=4, choices=[(x.name, x.value) for x in EventType])
    description = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        if self.location:
            self.geocode_location()
        super().save(*args, **kwargs)

    def geocode_location(self):
        nr = requests.get('https://nominatim.openstreetmap.org/reverse', params={'format': 'jsonv2', 'lat': self.location.y, 'lon': self.location.x, 'accept-language': 'en'})
        self.location_address = nr.json()['address']

    @property
    def location_text(self):
        if not self.location_address:
            return None
        addr = self.location_address
        return ", ".join(filter(lambda x: x is not None, [addr.get('village'), addr.get('town'), addr.get('city'), addr.get('state'), addr.get('country')]))

    @property
    def location_detailed_addr(self):
        # TODO: improve
        if not self.location_address:
            return None
        addr = self.location_address
        return ", ".join(filter(lambda x: x is not None, [addr.get('housenumber'), addr.get('street'), addr.get('village'), addr.get('city'), addr.get('state'), addr.get('country')]))

    class Meta:
        indexes = (
            models.Index(fields=('end',)),
        )


class EventParticipation(models.Model):
    event = models.ForeignKey('Event', null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey('User', null=True, on_delete=models.SET_NULL)


class User(AbstractUser):
    osm_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = 'osm_' + str(self.osm_id)
        super().save(*args, **kwargs)
