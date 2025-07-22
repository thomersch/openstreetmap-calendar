from xml.etree import ElementTree as ET

from django.contrib.gis.geos import Point
from requests_oauthlib import OAuth2Session


def get_user_attributes(session: OAuth2Session) -> dict:
    userreq = session.get("https://api.openstreetmap.org/api/0.6/user/details")

    userxml = ET.fromstring(userreq.text)
    userattrs = userxml.find("user").attrib

    attrs = {"osm_id": userattrs["id"], "display_name": userattrs["display_name"]}

    home = userxml.find("user/home")
    if home is not None:
        lat = home.attrib.get("lat", None)
        lon = home.attrib.get("lon", None)
        if lat and lon:
            attrs["home_location"] = Point(float(lon), float(lat))

    return attrs
