from datetime import timedelta
from textwrap import wrap
from typing import Iterable, List

from .models import Event


def encode_event(evt: Event) -> str:
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//OSM Calendar']
    lines += event_body(evt)
    lines += ['END:VCALENDAR']
    return '\r\n'.join(map(line_format, lines)) + '\r\n'


def encode_events(evts: Iterable[Event]) -> str:
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//OSM Calendar']
    for evt in evts:
        lines += event_body(evt)
    lines += ['END:VCALENDAR']
    return '\r\n'.join(map(line_format, lines)) + '\r\n'


def line_format(ln: str) -> str:
    return '\r\n\t'.join(wrap(ln.replace(',', '\,').replace('\n', '\\n'), 72, drop_whitespace=False))


def event_body(evt: Event) -> List[str]:
    lines = ['BEGIN:VEVENT']

    lines.append('UID:OSMCAL-{}'.format(evt.id))
    lines.append('DTSTAMP:{:%Y%m%dT%H%M%S}'.format(evt.start))
    if evt.whole_day:
        lines.append('DTSTART;VALUE=DATE:{:%Y%m%d}'.format(evt.start))
        if evt.end:
            lines.append('DTEND;VALUE=DATE:{:%Y%m%d}'.format(evt.end + timedelta(days=1)))
    else:
        lines.append('DTSTART:{:%Y%m%dT%H%M%S}'.format(evt.start))
        if evt.end:
            lines.append('DTEND:{:%Y%m%dT%H%M%S}'.format(evt.end))

    lines.append('SUMMARY:{}'.format(evt.name))
    if evt.description:
        lines.append('DESCRIPTION:{}'.format(evt.description))
    if evt.location:
        lines.append('GEO:{};{}'.format(evt.location.x, evt.location.y))
    if evt.location_address:
        lines.append('LOCATION:{}'.format(evt.location_detailed_addr))
    return lines + ['END:VEVENT']
