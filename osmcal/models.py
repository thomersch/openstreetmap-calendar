from enum import Enum

import bleach
import markdown
import requests
from background_task import background
from babel.dates import get_timezone_name
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db.models import PointField
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.text import Truncator
from pytz import timezone
from sentry_sdk import add_breadcrumb
from tzfpy import get_tz


class EventType(Enum):
    SOCI = "Social"
    MEET = "Meeting"
    WORK = "Work"
    MAPE = "Map Event"
    CONF = "Conference"


class Event(models.Model):
    name = models.CharField(max_length=200)

    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)
    whole_day = models.BooleanField(default=False)
    timezone = models.CharField(max_length=100, blank=True, null=True)

    location_name = models.CharField(max_length=50, blank=True, null=True)
    location = PointField(blank=True, null=True)
    location_address = models.JSONField(blank=True, null=True)

    link = models.URLField(blank=True, null=True)
    kind = models.CharField(
        max_length=4, choices=[(x.name, x.value) for x in EventType]
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text=mark_safe(
            'Tell people what the event is about and what they can expect. You may use <a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown</a> in this field.'
        ),
    )

    cancelled = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.location:
            self.geocode_location()

        # For the case that an event had previously an address which got removed by the edit:
        if not self.location:
            self.location_address = None

        super().save(*args, **kwargs)

    def geocode_location(self):
        try:
            self._geocode_location()
        except:
            event_id = self.id
            self._background_geocode_location(event_id)

    def _geocode_location(self):
        nr = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "format": "jsonv2",
                "lat": self.location.y,
                "lon": self.location.x,
                "accept-language": "en",
            },
            headers={"User-Agent": "osmcal"},
        )
        nr.raise_for_status()

        self.location_address = nr.json().get("address", None)
        if self.location_address is None:
            add_breadcrumb(category="nominatim", level="error", data=nr.json())

    @staticmethod
    @background(schedule=1)
    def _background_geocode_location(event_id):
        evt = Event.objects.get(id=event_id)
        evt.save()  # geocodes implicitly

    @property
    def location_text(self):
        if not self.location_address:
            return None
        addr = self.location_address
        return ", ".join(
            filter(
                lambda x: x is not None,
                [
                    addr.get("village"),
                    addr.get("town"),
                    addr.get("city"),
                    addr.get("state"),
                    addr.get("country"),
                ],
            )
        )

    @property
    def location_detailed_addr(self):
        # TODO: improve
        if not self.location_address:
            return None
        addr = self.location_address
        return ", ".join(
            filter(
                lambda x: x is not None,
                [
                    self.location_name,
                    addr.get("house_number"),
                    addr.get("road"),
                    addr.get("suburb"),
                    addr.get("village"),
                    addr.get("city"),
                    addr.get("state"),
                    addr.get("country"),
                ],
            )
        )

    @property
    def start_localized(self):
        tz = timezone(self.timezone)
        return self.start.astimezone(tz)

    @property
    def end_localized(self):
        if not self.end:
            return None
        tz = timezone(self.timezone)
        return self.end.astimezone(tz)

    @property
    def tz_name(self):
        return get_timezone_name(self.start_localized)

    @property
    def year_month(self):
        l = self.start_localized
        return (l.year, l.month)

    @property
    def short_description_without_markup(self) -> str:
        if not self.description:
            return ""
        max_words = 15
        cleaned = bleach.clean(markdown.markdown(self.description), tags=[], strip=True)
        return Truncator(cleaned).words(max_words)

    @property
    def originally_created_by(self) -> "User":
        return self.log.order_by("created_at").first().created_by

    class Meta:
        indexes = (models.Index(fields=("end",)),)


class AnswerType(Enum):
    TEXT = "Text Field"
    CHOI = "Choice"
    BOOL = "Boolean"


class ParticipationQuestion(models.Model):
    event = models.ForeignKey(
        "Event", null=True, on_delete=models.SET_NULL, related_name="questions"
    )
    question_text = models.CharField(max_length=200)
    answer_type = models.CharField(
        max_length=4, choices=[(x.name, x.value) for x in AnswerType]
    )
    mandatory = models.BooleanField(default=True)

    class Meta:
        ordering = ("event", "id")


class ParticipationQuestionChoice(models.Model):
    question = models.ForeignKey(
        ParticipationQuestion, related_name="choices", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=200)

    class Meta:
        ordering = ("question", "id")


class EventParticipation(models.Model):
    event = models.ForeignKey(
        "Event", null=True, on_delete=models.SET_NULL, related_name="participation"
    )
    user = models.ForeignKey("User", null=True, on_delete=models.SET_NULL)
    added_on = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        unique_together = ["event", "user"]


class ParticipationAnswer(models.Model):
    question = models.ForeignKey(
        ParticipationQuestion, on_delete=models.CASCADE, related_name="answers"
    )
    user = models.ForeignKey("User", null=True, on_delete=models.SET_NULL)
    answer = models.CharField(max_length=200)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("question", "user"), name="unique_question_answer"
            ),
        )


class EventLog(models.Model):
    event = models.ForeignKey("Event", related_name="log", on_delete=models.CASCADE)
    data = models.JSONField()
    created_by = models.ForeignKey("User", null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    osm_id = models.IntegerField(null=True)
    name = models.CharField(max_length=255)

    home_location = PointField(blank=True, null=True)

    is_moderator = models.BooleanField(default=False)

    def home_timezone(self):
        if not self.home_location:
            return None
        return tf.get_tz(self.home_location.x, self.home_location.y)

    def save(self, *args, **kwargs):
        if not self.username:
            if self.osm_id:
                self.username = "osm_" + str(self.osm_id)
            else:
                self.username = str(self.id)
        super().save(*args, **kwargs)
