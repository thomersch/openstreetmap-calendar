from django.contrib import admin
from django.urls import path

from django.conf.urls import include, url

from . import views

app_name = 'osmcal'

urlpatterns = [
    path('', views.Homepage.as_view(), name='homepage'),
    path('event/add/', views.event_edit, name='event-edit'),
    path('event/<int:event_id>/', views.event, name='event'),
    path('event/<int:event_id>.ics', views.EventICal.as_view(), name='event-ical'),
    path('event/<int:event_id>/change/', views.event_edit, name='event-change'),
    path('event/<int:event_id>/join/', views.JoinEvent.as_view(), name='event-join'),
    path('event/<int:event_id>/unjoin/', views.UnjoinEvent.as_view(), name='event-unjoin'),
    path('event/<int:event_id>/participants/', views.EventParticipants.as_view(), name='event-participants'),
    path('events.rss', views.EventFeed(), name='event-rss'),

    path('admin/', admin.site.urls),

    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    path('oauth/start/', views.oauth_start, name='oauth-start'),
    path('oauth/callback/', views.oauth_callback, name='oauth-callback'),

    path('documentation/', views.Documentation.as_view(), name='api-manual'),

    url('', include('django_prometheus.urls')),
]
