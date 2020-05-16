# from django.conf.urls import include, url
# from django.contrib import admin
from django.urls import path

from . import views

app_name = 'osmcal.community'

urlpatterns = [
    path('', views.CommunityList.as_view(), name='community-list'),
    path('create/', views.CommunityCreate.as_view(), name='community-create'),
]
