from xml.etree import ElementTree as ET

from django.conf import settings
from django.contrib.auth import login as dj_login
from django.http import HttpResponse
from django.shortcuts import redirect

from requests_oauthlib import OAuth1Session

from .models import User


def login(request):
    return HttpResponse("<a href='/oauth/start/'>Login using OSM</a>")


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
    return HttpResponse("hi!")
