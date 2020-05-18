from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View

from . import forms
from .models import Community


class CommunityList(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'osmcal/community/community_list.html', {
            'communities': Community.objects.annotate(member_count=Count('members')).order_by('-member_count')
        })


class CommunityCreate(View):
    def get(self, request, *args, **kwargs):
        form = forms.CommunityForm(label_suffix='')
        return render(request, 'osmcal/community/community_form.html', {'form': form})

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
        ctx = {
            'community': community,
            'user': request.user,
        }
        if not request.user.is_anonymous:
            ctx['is_member'] = community.members.filter(id=request.user.id).count() > 0

        return render(request, 'osmcal/community/community_detail.html', ctx)
