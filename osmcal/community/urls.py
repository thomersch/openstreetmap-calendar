# from django.conf.urls import include, url
# from django.contrib import admin
from django.urls import path

from . import views

app_name = "osmcal.community"

urlpatterns = [
    path("", views.CommunityList.as_view(), name="community-list"),
    path("create/", views.CommunityCreate.as_view(), name="community-create"),
    path("<int:community_id>/", views.CommunityDetail.as_view(), name="community"),
    path("<int:community_id>/join/", views.CommunityJoin.as_view(), name="community-join"),
    path("<int:community_id>/leave/", views.CommunityLeave.as_view(), name="community-leave"),
]
