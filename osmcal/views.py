from datetime import timedelta
from textwrap import wrap

from django.conf import settings
from django.contrib.auth import login as dj_login, logout as dj_logout
from django.contrib.auth.decorators import login_required
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.db.models import Q
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View

from requests_oauthlib import OAuth1Session
from xml.etree import ElementTree as ET

from . import forms
from .models import Event, User


def homepage(request):
    upcoming_events = Event.objects.filter(Q(start__gte=timezone.now()) | Q(end__gte=timezone.now())).order_by('start')

    filter_to_country = request.GET.get('in', None)
    if filter_to_country:
        upcoming_events = upcoming_events.filter(location_address__country=filter_to_country)

    filter_around = request.GET.get('around', None)
    if filter_around:
        filter_around = [float(x) for x in filter_around.split(',')]
        pt = Point(filter_around[1], filter_around[0], srid=4326)
        upcoming_events = upcoming_events.annotate(distance=Distance('location', pt)).filter(distance__lte=50000) # distance in meter

    country_list = Event.objects.order_by('location_address__country').filter(location_address__country__isnull=False).values_list('location_address__country', flat=True).distinct()

    return render(request, 'osmcal/homepage.html', context={'user': request.user, 'events': upcoming_events, 'country_list': country_list, 'filter': {'in': filter_to_country, 'around': filter_around}})


def event(request, event_id):
    event = Event.objects.get(id=event_id)
    return render(request, 'osmcal/event.html', context={'event': event})


def login(request):
    return render(request, 'osmcal/login.html', context={'next': request.GET.get('next', None)})


def logout(request):
    dj_logout(request)
    return redirect("/")


@login_required
def event_edit(request, event_id=None):
    form = forms.EventForm()
    if event_id is not None:
        form = forms.EventForm(instance=Event.objects.get(id=event_id))

    if request.method == 'POST':
        form = forms.EventForm(request.POST)
        if event_id is not None:
            form = forms.EventForm(request.POST, instance=Event.objects.get(id=event_id))

        if form.is_valid():
            if event_id is None:
                evt = Event.objects.create(**form.cleaned_data)
                evt.created_by = request.user
                evt.save()
            else:
                form.save()
            return redirect(reverse('event', kwargs={'event_id': event_id or evt.id}))

    return render(request, 'osmcal/event_form.html', context={'form': form})


class EventICal(View):
    def ical_line_format(self, ln):
        return '\r\n\t'.join(wrap(ln.replace(',', '\,').replace('\n', '\\n'), 72, drop_whitespace=False))

    def get(self, request, event_id):
        evt = Event.objects.get(id=event_id)

        lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//OSM Calendar', 'BEGIN:VEVENT']
        lines.append('UID:OSMCAL-{}'.format(evt.id))

        lines.append('DTSTAMP:{:%Y%m%dT%H%M%S}'.format(evt.start))
        if evt.whole_day:
            lines.append('DTSTART;VALUE=DATE:{:%Y%m%d}'.format(evt.start))
            if evt.end:
                lines.append('DTEND;VALUE=DATE:{:%Y%m%d}'.format(evt.end + timedelta(days=1)))
        else:
            lines.append('DTSTART:{:%Y%m%dT%H%M%S}'.format(evt.start))
            if evt.end:
                lines.append('DTEND:{:%Y%m%dT%H%M%S}'.format(evt.end))

        lines.append('SUMMARY:{}'.format(evt.name))
        if evt.description:
            lines.append('DESCRIPTION:{}'.format(evt.description))
        if evt.location:
            lines.append('GEO:{};{}'.format(evt.location.x, evt.location.y))
        if evt.location_address:
            lines.append('LOCATION:{}'.format(evt.location_detailed_addr))
        lines += ['END:VEVENT', 'END:VCALENDAR']
        return HttpResponse('\r\n'.join(map(self.ical_line_format, lines)) + '\r\n', content_type="text/calendar")


def oauth_start(request):
    osm = OAuth1Session(
        settings.OAUTH_OPENSTREETMAP_KEY,
        client_secret=settings.OAUTH_OPENSTREETMAP_SECRET
    )
    req_token = osm.fetch_request_token('https://www.openstreetmap.org/oauth/request_token')
    request.session['oauth_params'] = req_token
    if request.GET.get('next', None):
        request.session['next'] = request.GET['next']
    auth_url = osm.authorization_url('https://www.openstreetmap.org/oauth/authorize')
    return redirect(auth_url)


def oauth_callback(request):
    osm = OAuth1Session(
        settings.OAUTH_OPENSTREETMAP_KEY,
        client_secret=settings.OAUTH_OPENSTREETMAP_SECRET,
        resource_owner_key=request.session.get("oauth_params")["oauth_token"],
        resource_owner_secret=request.session.get("oauth_params")["oauth_token_secret"],
        verifier='OSMNOPE'
    )
    osm.fetch_access_token('https://www.openstreetmap.org/oauth/access_token')
    userreq = osm.get('https://api.openstreetmap.org/api/0.6/user/details')

    userxml = ET.fromstring(userreq.text)
    userattrs = userxml.find('user').attrib

    try:
        u = User.objects.get(osm_id=userattrs["id"])
    except User.DoesNotExist:
        u = User.objects.create(osm_id=userattrs["id"])
    u.name = userattrs['display_name']
    u.save()

    dj_login(request, u)
    request.session.delete("oauth_params")

    next_redir = request.session.pop('next', None)
    if next_redir:
        return redirect(next_redir)
    return redirect('/login/')
