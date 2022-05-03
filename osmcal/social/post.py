from background_task import background
from osmcal.models import Event
from osmcal.social import twitter
from osmcal.templatetags import locadate


def assemble_msg(evt_id):
    evt = Event.objects.get(id=evt_id)

    return "{} on {} https://osmcal.org/event/{}/".format(
        evt.name,
        locadate.short_date_format(evt),
        evt.id
    )


@background(schedule=5)
def announce_event_now(evt_id):
    msg = assemble_msg(evt_id)
    twitter.post(msg)


def announce_event(instance, created, **kwargs):
    if not created:
        return

    announce_event_now(instance.id)
