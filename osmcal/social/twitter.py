import requests
from django.conf import settings
from requests_oauthlib import OAuth1, OAuth1Session

base_authorization_url = 'https://api.twitter.com/oauth/authorize'
request_token_url = 'https://api.twitter.com/oauth/request_token'
access_token_url = 'https://api.twitter.com/oauth/access_token'
tweet_url = 'https://api.twitter.com/1.1/statuses/update.json'


def _get_config_value(key, default=None):
    return settings.SOCIAL['twitter'].get(key, None)


def auth_initialize():
    session = OAuth1Session(
        _get_config_value('client_key'),
        _get_config_value('client_secret')
    )
    req_tokens = session.fetch_request_token(
        request_token_url,
        data={'x_auth_access_type': 'write'}
    )
    print("Request tokens:", req_tokens)
    auth_url = session.authorization_url(base_authorization_url)
    print("Go to {} and authorize please".format(auth_url))


def auth_keys(verifier):
    session = OAuth1(
        _get_config_value('client_key'),
        client_secret=_get_config_value('client_secret'),
        resource_owner_key=_get_config_value('user_key'),
        resource_owner_secret=_get_config_value('user_secret'),
        verifier=verifier
    )
    print(requests.post(access_token_url, auth=session).content)


def post(text: str):
    oauth = OAuth1(
        _get_config_value('client_key'),
        client_secret=_get_config_value('client_secret'),
        resource_owner_key=_get_config_value('user_key'),
        resource_owner_secret=_get_config_value('user_secret')
    )
    return requests.post(tweet_url, data={'status': text}, auth=oauth)
