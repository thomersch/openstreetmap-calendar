from datetime import datetime

import pytz
from django.contrib.auth import get_user_model
from django.forms import formset_factory
from django.test import Client, TestCase

from osmcal import forms
from osmcal.models import Event

User = get_user_model()


def event_form_data(**overrides):
    # Defaults every EventForm/QuestionFormSet field to "", so adding a
    # field to either form doesn't silently break callers.
    data = {name: "" for name in forms.EventForm().fields}

    management_form = formset_factory(forms.QuestionForm, extra=0)(prefix="questions").management_form
    data.update({management_form.add_prefix(k): v for k, v in management_form.initial.items()})

    data.update(overrides)
    return data


class AuthenticatedTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client = Client()
        self.client.login(username="testuser", password="testpass")


class DuplicateEventTest(AuthenticatedTestCase):
    def test_duplicate_preserves_timezone(self):
        tz = "Europe/Berlin"
        original = Event.objects.create(
            name="Berlin Meetup",
            start=pytz.timezone(tz).localize(datetime(2027, 6, 15, 18, 0)),
            kind="MEET",
            timezone=tz,
        )

        resp = self.client.post(
            f"/event/{original.id}/duplicate/",
            event_form_data(
                name=original.name,
                start="2027-09-20 18:00:00",
                kind=original.kind,
                timezone=tz,
            ),
        )

        self.assertEqual(resp.status_code, 302)
        duplicated = Event.objects.exclude(id=original.id).get(name=original.name)
        self.assertEqual(duplicated.timezone, tz)

    def test_duplicate_get_carries_over_utc_timezone(self):
        # Reproduces issue #88: duplicating an event without a location, but
        # with timezone set to UTC, dropped the timezone setting because the
        # widget rendered the field as hidden/blank instead of pre-selecting UTC.
        original = Event.objects.create(
            name="UTC Meetup",
            start=pytz.UTC.localize(datetime(2027, 6, 15, 18, 0)),
            kind="MEET",
            # This is the value the form actually stores for "UTC": babel
            # normalizes it to "Etc/UTC", which isn't in pytz.common_timezones.
            timezone="Etc/UTC",
        )

        resp = self.client.get(f"/event/{original.id}/duplicate/")

        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        self.assertIn("<option selected>UTC</option>", content)
        select_start = content.index("<select")
        select_end = content.index(">", select_start)
        self.assertNotIn("hidden", content[select_start:select_end])


class EditEventTimezoneTest(AuthenticatedTestCase):
    def test_edit_utc_event_shows_timezone_field(self):
        evt = Event.objects.create(
            name="UTC Meetup",
            start=pytz.UTC.localize(datetime(2027, 6, 15, 18, 0)),
            kind="MEET",
            # This is the value the form actually stores for "UTC": babel
            # normalizes it to "Etc/UTC", which isn't in pytz.common_timezones.
            timezone="Etc/UTC",
        )

        resp = self.client.get(f"/event/{evt.id}/change/")

        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        # The <select> must not be hidden, and "UTC" must be the selected option,
        # otherwise the timezone field appears blank when editing (issue #202).
        self.assertIn("<option selected>UTC</option>", content)
        select_start = content.index("<select")
        select_end = content.index(">", select_start)
        self.assertNotIn("hidden", content[select_start:select_end])


class EventListTest(TestCase):
    def test_location_out_of_range(self):
        # Based on Sentry report OSM-CALENDAR-1W
        c = Client()
        resp = c.get("/events.ics?around=5564")  # The around parameter obviously doesn't make any sense.
        self.assertEqual(resp.status_code, 400)

    def test_location_radius_out_of_range(self):
        c = Client()
        resp = c.get("/events.ics?around=52,13&around_radius=260")  # The around radius parameter is too large.
        self.assertEqual(resp.status_code, 400)

    def test_location_around_50k(self):
        c = Client()
        resp = c.get("/events.ics?around=52,13")
        self.assertEqual(resp.status_code, 200)

    def test_location_bad_syntax(self):
        c = Client()
        resp = c.get("/events.ics?around=52\\,13")
        self.assertEqual(resp.status_code, 400)

    def test_location_around_dist(self):
        c = Client()
        resp = c.get("/events.ics?around=52,13&around_radius=5")
        self.assertEqual(resp.status_code, 200)
