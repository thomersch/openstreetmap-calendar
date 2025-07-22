from django.test import Client, TestCase


class EventListTest(TestCase):
    def test_location_out_of_range(self):
        # Based on Sentry report OSM-CALENDAR-1W
        c = Client()
        resp = c.get("/events.ics?around=5564")  # The around parameter obviously doesn't make any sense.
        self.assertEqual(resp.status_code, 400)

    def test_location_radius_out_of_range(self):
        c = Client()
        resp = c.get("/events.ics?around=52,13&around_radius=260")  # The around radius parameter is too large.
        self.assertEqual(resp.status_code, 400)

    def test_location_around_50k(self):
        c = Client()
        resp = c.get("/events.ics?around=52,13")
        self.assertEqual(resp.status_code, 200)

    def test_location_bad_syntax(self):
        c = Client()
        resp = c.get("/events.ics?around=52\\,13")
        self.assertEqual(resp.status_code, 400)

    def test_location_around_dist(self):
        c = Client()
        resp = c.get("/events.ics?around=52,13&around_radius=5")
        self.assertEqual(resp.status_code, 200)
