import json

from django import template
from django.utils.safestring import mark_safe
from osmcal.models import Event

register = template.Library()


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

    if evt.location:
        addr = {
            "@type": "PostalAddress",
            "addressLocality": ", ".join(
                filter(
                    lambda x: x is not None,
                    [
                        evt.location_address.get("village"),
                        evt.location_address.get("town"),
                        evt.location_address.get("city"),
                    ],
                )
            ),
        }
        if "country_code" in evt.location_address:
            addr["addressCountry"] = evt.location_address.get("country_code").upper()
        if "state" in evt.location_address:
            addr["addressRegion"] = evt.location_address.get("state")
        if "postcode" in evt.location_address:
            addr["postalCode"] = evt.location_address.get("postcode")
        if "road" in evt.location_address:
            addr["streetAddress"] = ", ".join(
                filter(
                    lambda x: x is not None,
                    [evt.location_address.get("house_number"), evt.location_address.get("road")],
                )
            )

        data["location"] = {
            "@type": "Place",
            "latitude": evt.location.y,
            "longitude": evt.location.x,
            "address": addr,
        }
        if evt.location_name:
            data["location"]["name"] = evt.location_name

    if evt.link:
        data["url"] = evt.link

    return mark_safe("""<script type="application/ld+json">{}</script>""".format(json.dumps(data)))
