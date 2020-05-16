from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from .models import Community


class CommunityList(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'osmcal/community/community_list.html', {'communities': Community.objects.all()})


class CommunityCreate(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'osmcal/community/community_form.html', {})
