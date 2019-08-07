from xml.etree import ElementTree as ET

from django.conf import settings
from django.contrib.auth import login as dj_login, logout as dj_logout
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.db.models import Q
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from requests_oauthlib import OAuth1Session

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
    if request.user.is_authenticated:
        # TODO
        return HttpResponse("You are logged in as {}. <a href='/'>Go to homepage.</a>".format(request.user.name))
    return HttpResponse("<a href='/oauth/start/'>Login using OSM</a>")


def logout(request):
    dj_logout(request)
    return redirect("/")


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


def oauth_start(request):
    osm = OAuth1Session(
        settings.OAUTH_OPENSTREETMAP_KEY,
        client_secret=settings.OAUTH_OPENSTREETMAP_SECRET
    )
    req_token = osm.fetch_request_token('https://www.openstreetmap.org/oauth/request_token')
    request.session["oauth_params"] = req_token
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
    return redirect('/login/')
