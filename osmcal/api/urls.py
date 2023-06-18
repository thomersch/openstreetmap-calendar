from django.urls import path

from . import compatviews, views

app_name = "osmcal.api"

urlpatterns = [
    path("v1/events/", compatviews.EventListV1.as_view(), name="api-event-list"),
    path("v1/events/past/", compatviews.PastEventListV1.as_view(), name="api-past-event-list"),
    path("v2/events/", views.EventList.as_view(), name="api-event-list-v2"),
    path("v2/events/past/", views.PastEventList.as_view(), name="api-past-event-list-v2"),
    path("internal/timezone", views.Timezone.as_view(), name="api-internal-timezone"),
]
