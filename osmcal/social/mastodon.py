import requests
from django.conf import settings

post_status_url = "https://en.osm.town/api/v1/statuses"


def _get_config_value(key, default=None):
    return settings.SOCIAL["mastodon"].get(key, None)


def post(text: str):
    resp = requests.post(
        post_status_url,
        headers={"Authorization": f"Bearer {_get_config_value('access_token')}"},
        data={"status": text},
    )
    resp.raise_for_status()
