# from django.conf.urls import include, url
# from django.contrib import admin
from django.urls import path

from . import views

app_name = 'osmcal.api'

urlpatterns = [
    path('v1/events/', views.EventList.as_view(), name='api-event-list'),
    path('v1/events/past/', views.PastEventList.as_view(), name='api-past-event-list'),
]
