from django.conf import settings
from django.urls import include, path

from . import views

app_name = 'osmcal'

urlpatterns = [
    path('', views.Homepage.as_view(), name='homepage'),
    path('subscribe/', views.SubscriptionInfo.as_view(), name='subscription-info'),

    path('event/add/', views.EditEvent.as_view(), name='event-edit'),
    path('event/<int:event_id>/', views.event, name='event'),
    path('event/<int:event_id>.ics', views.EventICal.as_view(), name='event-ical'),
    path('event/<int:event_id>/cancel/', views.CancelEvent.as_view(), name='event-cancel'),
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

    path('me/', views.CurrentUserView.as_view(), name='user-self'),

    path('', include('django_prometheus.urls')),
    path('api/', include('osmcal.api.urls')),
    path('community/', include('osmcal.community.urls'))
]

if settings.DEBUG:
    urlpatterns.append(
        path('login/mock/', views.MockLogin.as_view(), name='login-mock')
    )
