from django.tasks import task


@task
def background_geocode_location(event_id):
    from osmcal.models import Event  # noqa

    evt = Event.objects.get(id=event_id)
    evt.save()  # geocodes implicitly
