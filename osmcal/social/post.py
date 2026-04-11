from django.tasks import task

from osmcal.models import Event
from osmcal.social import mastodon
from osmcal.templatetags import locadate


def assemble_msg(evt_id):
    evt = Event.objects.get(id=evt_id)

    return "{} on {} https://osmcal.org/event/{}/".format(evt.name, locadate.short_date_format(evt), evt.id)


@task
def announce_event_now(evt_id):
    msg = assemble_msg(evt_id)
    mastodon.post(msg)


def announce_event(instance, created, **kwargs):
    if not created:
        return

    announce_event_now.enqueue(instance.id)
