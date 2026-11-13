import json
from unittest import mock

from django.contrib.sessions.models import Session
from django.test import TestCase, override_settings

from osmcal.views import OAUTH_FLOW_COOKIE


@override_settings(OAUTH2_OPENSTREETMAP_CLIENT_ID="test-client", DEBUG=False)
class OAuthFlowTest(TestCase):
    def test_start_sets_signed_cookie_without_creating_session(self):
        response = self.client.get("/oauth/start/?next=/event/1/")

        self.assertEqual(response.status_code, 302)
        self.assertIn(OAUTH_FLOW_COOKIE, response.cookies)
        self.assertTrue(response.cookies[OAUTH_FLOW_COOKIE]["httponly"])
        self.assertNotIn("sessionid", response.cookies)
        self.assertEqual(Session.objects.count(), 0)

    def test_callback_without_cookie_is_rejected(self):
        response = self.client.get("/oauth/callback/?code=x&state=y")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Session.objects.count(), 0)

    def test_callback_with_tampered_cookie_is_rejected(self):
        self.client.cookies[OAUTH_FLOW_COOKIE] = json.dumps({"state": "s", "next": None})

        response = self.client.get("/oauth/callback/?code=x&state=s")

        self.assertEqual(response.status_code, 400)

    def _complete_flow(self, next_param):
        start = self.client.get("/oauth/start/", {"next": next_param} if next_param else {})
        state = mock.sentinel.state
        self.client.cookies[OAUTH_FLOW_COOKIE] = start.cookies[OAUTH_FLOW_COOKIE].value
        attrs = {"osm_id": 4242, "display_name": "tester"}
        with (
            mock.patch("osmcal.views.oauth.get_authenticated_session") as get_session,
            mock.patch("osmcal.views.osmuser.get_user_attributes", return_value=attrs),
        ):
            response = self.client.get("/oauth/callback/?code=x&state=y")
        return response, get_session, state

    def test_callback_logs_in_and_redirects_to_next(self):
        response, get_session, _ = self._complete_flow("/event/1/")

        self.assertRedirects(response, "/event/1/", fetch_redirect_response=False)
        self.assertIn("_auth_user_id", self.client.session)
        self.assertEqual(Session.objects.count(), 1)
        self.assertEqual(response.cookies[OAUTH_FLOW_COOKIE]["max-age"], 0)
        self.assertTrue(get_session.call_args.kwargs["state"])

    def test_callback_ignores_foreign_next(self):
        response, _, _ = self._complete_flow("https://evil.example/")

        self.assertRedirects(response, "/login/", fetch_redirect_response=False)
