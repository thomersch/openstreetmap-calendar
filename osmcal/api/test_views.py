from django.test import Client, TestCase


class APIBaseTest(TestCase):
    def test_cors(self):
        c = Client()
        resp = c.options('/api/v1/events/')

        self.assertTrue(resp.has_header('access-control-allow-headers'))
        self.assertTrue(resp.get('access-control-allow-origin', '*'))
