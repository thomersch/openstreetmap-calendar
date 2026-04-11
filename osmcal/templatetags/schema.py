import json

from django import template
from django.utils.safestring import mark_safe
from osmcal.models import Event

register = template.Library()


def _build_address(location_address):
    addr = {
        "@type": "PostalAddress",
        "addressLocality": ", ".join(
            filter(
                lambda x: x is not None,
                [
                    location_address.get("village"),
                    location_address.get("town"),
                    location_address.get("city"),
                ],
            )
        ),
    }
    if "country_code" in location_address:
        addr["addressCountry"] = location_address["country_code"].upper()
    if "state" in location_address:
        addr["addressRegion"] = location_address["state"]
    if "postcode" in location_address:
        addr["postalCode"] = location_address["postcode"]
    if "road" in location_address:
        addr["streetAddress"] = ", ".join(
            filter(
                lambda x: x is not None,
                [location_address.get("house_number"), location_address["road"]],
            )
        )
    return addr


def _build_location(evt):
    addr = _build_address(evt.location_address) if evt.location_address else None
    if not (addr or evt.location or evt.location_name):
        return None
    place = {"@type": "Place"}
    if evt.location:
        place["latitude"] = evt.location.y
        place["longitude"] = evt.location.x
    if addr:
        place["address"] = addr
    if evt.location_name:
        place["name"] = evt.location_name
    return place


@register.simple_tag()
def schema_block(evt):
    if not isinstance(evt, Event):
        raise TypeError("parameter needs to be an event")
    data = {
        "@context": "https://schema.org",
        "@type": "Event",
        "startDate": evt.start_localized.isoformat(),
        "name": evt.name,
    }
    if evt.end:
        data["endDate"] = evt.end_localized.isoformat()
    if evt.description:
        data["description"] = evt.description

    if evt.cancelled:
        data["eventStatus"] = "https://schema.org/EventCancelled"
    else:
        data["eventStatus"] = "https://schema.org/EventScheduled"

    location = _build_location(evt)
    if location:
        data["location"] = location

    if evt.link:
        data["url"] = evt.link

    return mark_safe("""<script type="application/ld+json">{}</script>""".format(json.dumps(data)))
