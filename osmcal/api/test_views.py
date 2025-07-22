from datetime import datetime

from django.test import Client, TestCase


class APIBaseTest(TestCase):
    def test_cors(self):
        c = Client()
        resp = c.options("/api/v1/events/")

        self.assertTrue(resp.has_header("access-control-allow-headers"))
        self.assertTrue(resp.get("access-control-allow-origin", "*"))

    def test_past(self):
        c = Client()
        resp = c.get("/api/v1/events/past/")
        self.assertEqual(resp.status_code, 200)


class APIV1Test(TestCase):
    fixtures = ["demo"]

    def test_structure_v1(self):
        """
        This test ensures that the structure of the API response does not change.
        """
        c = Client()
        resp = c.get("/api/v1/events/")

        evts = resp.json()
        self.assertNotEqual(len(evts), 0)

        for evt in evts:
            self.assertIn("name", evt)
            self.assertIn("url", evt)
            self.assertIn("date", evt)

            self.assertIn("start", evt["date"])
            self.assertIn("human", evt["date"])
            self.assertIn("whole_day", evt["date"])

            datetime.strptime(evt["date"]["start"], "%Y-%m-%d %H:%M:%S")

            if "location" in evt:
                self.assertIn("coords", evt["location"])


class APIV2Test(TestCase):
    fixtures = ["demo"]

    def test_structure_v2(self):
        c = Client()
        resp = c.get("/api/v2/events/")

        evts = resp.json()
        self.assertNotEqual(len(evts), 0)

        for evt in evts:
            self.assertIn("name", evt)
            self.assertIn("url", evt)
            self.assertIn("date", evt)

            self.assertIn("start", evt["date"])
            self.assertIn("human", evt["date"])
            self.assertIn("whole_day", evt["date"])

            datetime.fromisoformat(evt["date"]["start"])

            if "location" in evt:
                self.assertIn("coords", evt["location"])
