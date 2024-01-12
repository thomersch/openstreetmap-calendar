from django.conf import settings
from django.urls import reverse
from requests_oauthlib import OAuth2Session


def get_oauth_session(request):
    callback_uri = request.build_absolute_uri(reverse("oauth-callback"))
    if settings.DEBUG:
        # This simplifies the reverse proxy setup on dev:
        # It's pretending we're using HTTPS with a correct configuration.
        callback_uri = callback_uri.replace("http", "https")

    return OAuth2Session(
        settings.OAUTH2_OPENSTREETMAP_CLIENT_ID,
        redirect_uri=callback_uri,
        scope=["read_prefs"],
    )


def get_authenticated_session(request) -> OAuth2Session:
    authorization_response = request.get_raw_uri()
    if settings.DEBUG:
        # This simplifies the reverse proxy setup on dev:
        # It's pretending we're using HTTPS with a correct configuration.
        authorization_response = authorization_response.replace("http", "https")

    osm = get_oauth_session(request)
    osm.fetch_token(
        "https://www.openstreetmap.org/oauth2/token",
        client_secret=settings.OAUTH2_OPENSTREETMAP_CLIENT_SECRET,
        authorization_response=authorization_response,
    )
    return osm
