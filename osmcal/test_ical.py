from datetime import datetime

from django.test import TestCase

from .ical import encode_event, encode_events
from .models import Event


class IcalEncodeTest(TestCase):
    def test_single_event(self):
        evt = Event.objects.create(
            id=12,
            start=datetime(year=2032, month=1, day=3, hour=12, minute=00),
            end=datetime(year=2032, month=1, day=3, hour=14, minute=00),
            timezone="UTC",
        )
        self.assertIsInstance(encode_event(evt), str)

    def test_multiple_events(self):
        Event.objects.create(
            name="First EVT",
            start=datetime(year=2021, month=1, day=3, hour=12, minute=00),
            end=datetime(year=2021, month=1, day=3, hour=14, minute=00),
            timezone="Europe/Berlin",
        )
        Event.objects.create(
            name="Some Event",
            start=datetime(year=2021, month=1, day=4, hour=12, minute=00),
            end=datetime(year=2021, month=1, day=4, hour=14, minute=00),
            timezone="Europe/Berlin",
        )

        ics = encode_events(Event.objects.all())
        self.assertIsInstance(ics, str)
