from django.contrib import admin
from django.urls import path

# from django.conf.urls import url

from . import views

app_name = 'osmcal'

urlpatterns = [
    path('', views.Homepage.as_view()),
    path('event/add/', views.event_edit),
    path('event/<int:event_id>/', views.event, name='event'),
    path('event/<int:event_id>.ics', views.EventICal.as_view(), name='event-ical'),
    path('event/<int:event_id>/change/', views.event_edit, name='event-change'),
    path('events.rss', views.EventFeed()),

    path('admin/', admin.site.urls),

    path('login/', views.login),
    path('logout/', views.logout),

    path('oauth/start/', views.oauth_start),
    path('oauth/callback/', views.oauth_callback)
]
