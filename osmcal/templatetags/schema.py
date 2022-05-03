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
		"startDate": evt.start.isoformat(),
		"name": evt.name
	}
	if evt.end:
		data["endDate"] = evt.end.isoformat()

	if evt.cancelled:
		data["eventStatus"] = "https://schema.org/EventCancelled"
	else:
		data["eventStatus"] = "https://schema.org/EventScheduled"

	if evt.location:
		data["location"] = {
			"latitude": evt.location.y,
			"longitude": evt.location.x,
			"address": evt.location_detailed_addr
		}

	if evt.link:
		data["url"] = evt.link

	return mark_safe("""<script type="application/ld+json">{}</script>""".format(json.dumps(data)))
