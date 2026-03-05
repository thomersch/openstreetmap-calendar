from datetime import timedelta
from typing import Iterable

import pytz
from icalendar import Calendar, Event as VEvent, vDate, vGeo

from .models import Event


def _build_calendar() -> Calendar:
    cal = Calendar()
    cal.add("version", "2.0")
    cal.add("prodid", "-//OSM Calendar")
    return cal


def _build_vevent(evt: Event) -> VEvent:
    vevent = VEvent()
    vevent.add("uid", "OSMCAL-{}".format(evt.id))
    vevent.add("dtstamp", evt.start_localized)

    if evt.cancelled:
        vevent.add("status", "CANCELLED")

    if evt.whole_day:
        vevent.add("dtstart", vDate(evt.start_localized.date()))
        if evt.end:
            vevent.add("dtend", vDate((evt.end_localized + timedelta(days=1)).date()))
    else:
        tz = pytz.timezone(str(evt.timezone))
        vevent.add("dtstart", evt.start_localized.astimezone(tz))
        if evt.end:
            vevent.add("dtend", evt.end_localized.astimezone(tz))

    vevent.add("summary", evt.name)

    description = evt.description or ""
    if evt.link:
        description += "\n" + "Event Website: " + evt.link
    if description:
        vevent.add("description", description)

    if evt.location:
        vevent.add("geo", vGeo((evt.location.y, evt.location.x)))
    if evt.location_address:
        vevent.add("location", evt.location_detailed_addr)

    return vevent


def encode_event(evt: Event) -> str:
    cal = _build_calendar()
    cal.add_component(_build_vevent(evt))
    return cal.to_ical().decode("utf-8")


def encode_events(evts: Iterable[Event]) -> str:
    cal = _build_calendar()
    for evt in evts:
        cal.add_component(_build_vevent(evt))
    return cal.to_ical().decode("utf-8")
