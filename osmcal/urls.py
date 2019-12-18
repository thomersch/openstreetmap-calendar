from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path

from . import views

app_name = 'osmcal'

urlpatterns = [
    path('', views.Homepage.as_view(), name='homepage'),
    path('event/add/', views.EditEvent.as_view(), name='event-edit'),

    path('event/<int:event_id>/', views.event, name='event'),
    path('event/<int:event_id>.ics', views.EventICal.as_view(), name='event-ical'),
    path('event/<int:event_id>/change/', views.EditEvent.as_view(), name='event-change'),
    path('event/<int:event_id>/duplicate/', views.DuplicateEvent.as_view(), name='event-duplicate'),

    path('event/<int:event_id>/join/', views.JoinEvent.as_view(), name='event-join'),
    path('event/<int:event_id>/unjoin/', views.UnjoinEvent.as_view(), name='event-unjoin'),
    path('event/<int:event_id>/participants/', views.EventParticipants.as_view(), name='event-participants'),

    path('events/past/', views.PastEvents.as_view(), name='events-past'),
    path('events/past/<int:page>/', views.PastEvents.as_view(), name='events-past'),
    path('events.rss', views.EventFeed(), name='event-rss'),
    path('events.ics', views.EventFeedICal.as_view(), name='event-feed-ical'),

    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    path('oauth/start/', views.oauth_start, name='oauth-start'),
    path('oauth/callback/', views.oauth_callback, name='oauth-callback'),

    path('documentation/', views.Documentation.as_view(), name='api-manual'),

    url('', include('django_prometheus.urls')),
    url('api/', include('osmcal.api.urls')),
]
