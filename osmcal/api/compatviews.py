from .compatserializers import EventsV1Serializer
from .views import EventList, PastEventList

"""Views that implement older versions of the API."""


class EventListV1(EventList):
    def get_serializer(self):
        return EventsV1Serializer


class PastEventListV1(PastEventList):
    def get_serializer(self):
        return EventsV1Serializer
