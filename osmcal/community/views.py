from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from osmcal.models import Event

from . import forms
from .models import Community


class CommunityList(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'osmcal/community/community_list.html', {
            'communities': Community.objects.annotate(member_count=Count('members')).order_by('-member_count')
        })


class CommunityCreate(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form = forms.CommunityForm(label_suffix='')
        return render(request, 'osmcal/community/community_form.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = forms.CommunityForm(request.POST)
        form.is_valid()
        c = Community.objects.create(**form.cleaned_data)
        c.members.add(request.user)
        c.save()
        return HttpResponse(c.id)


class CommunityDetail(View):
    def get(self, request, community_id):
        community = get_object_or_404(Community, id=community_id)
        now = timezone.now()
        upcoming_events = Event.objects.filter(community=community).filter(Q(start__gte=now) | Q(end__gte=now)).order_by('start')

        ctx = {
            'community': community,
            'user': request.user,
            'events': upcoming_events
        }
        if not request.user.is_anonymous:
            ctx['is_member'] = community.members.filter(id=request.user.id).count() > 0

        return render(request, 'osmcal/community/community_detail.html', ctx)


class CommunityJoin(View):
    @method_decorator(login_required)
    def get(self, request, community_id):
        community = get_object_or_404(Community, id=community_id)
        return render(request, 'osmcal/community/community_join.html', context={'community': community})

    @method_decorator(login_required)
    def post(self, request, community_id):
        community = get_object_or_404(Community, id=community_id)
        community.members.add(request.user)
        community.save()
        return redirect(reverse('osmcal.community:community', args=[community_id]))


class CommunityLeave(View):
    @method_decorator(login_required)
    def get(self, request, community_id):
        community = get_object_or_404(Community, id=community_id)
        return render(request, 'osmcal/community/community_leave.html', context={'community': community})

    @method_decorator(login_required)
    def post(self, request, community_id):
        community = get_object_or_404(Community, id=community_id)
        community.members.remove(request.user)
        return redirect(reverse('osmcal.community:community', args=[community_id]))
