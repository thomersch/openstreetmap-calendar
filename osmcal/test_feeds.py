from django.test import Client, TestCase


class FeedBaseTest(TestCase):
    def test_rss_base(self):
        c = Client()
        resp = c.get("/events.rss")

        self.assertEqual(resp.status_code, 200)
