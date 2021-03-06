from django.db import migrations
from pytz import timezone
from timezonefinder import TimezoneFinder


def set_timezones(apps, schema_editor):
    tf = TimezoneFinder()
    Event = apps.get_model('osmcal', 'Event')
    for event in Event.objects.filter(timezone=None):
        if event.location:
            tz = tf.timezone_at(lng=event.location.x, lat=event.location.y)
            if tz is not None:
                event.timezone = tz
        if not event.timezone:
            # Either time zone could not be determined from location or no location is available.
            event.timezone = 'UTC'
        tz = timezone(event.timezone)
        event.start = tz.localize(event.start.replace(tzinfo=None))

        if event.end:
            event.end = tz.localize(event.end.replace(tzinfo=None))
        event.save()


class Migration(migrations.Migration):

    dependencies = [
        ('osmcal', '0026_event_timezone'),
    ]

    operations = [
        migrations.RunPython(set_timezones)
    ]
