from datetime import datetime

from django.template.loader import render_to_string
from django.test import SimpleTestCase
from django.utils import translation

# from .models import Event


class MockEvent(object):
    def __init__(self, start, end=None, whole_day=False, location='Dummy'):
        self.start = start
        self.end = end
        self.whole_day = whole_day
        self.timezone = 'UTC'
        self.location = location


class DateFormatTest(SimpleTestCase):
    def _fmt(self, evt):
        return render_to_string('osmcal/date.txt', {'event': evt}).strip()

    def _fmt_loca(self, evt):
        return render_to_string('osmcal/date.l10n.txt', {'event': evt}).strip()

    def setUp(self):
        self.cur = datetime.now()

    def test_dateformat_start(self):
        self.assertEqual(
            self._fmt(MockEvent(start=datetime(year=self.cur.year, month=1, day=1), whole_day=True)),
            '1st January'
        )

    def test_dateformat_start_with_time(self):
        self.assertEqual(
            self._fmt(MockEvent(start=datetime(year=self.cur.year, month=1, day=1, hour=18))),
            '1st January 18:00'
        )

    def test_dateformat_start_end_with_time(self):
        self.assertEqual(
            self._fmt(MockEvent(start=datetime(year=self.cur.year, month=1, day=2, hour=16), end=datetime(year=self.cur.year, month=1, day=2, hour=18))),
            '2nd January 16:00 – 18:00'
        )

    def test_dateformat_start_end_with_time_multiday(self):
        self.assertEqual(
            self._fmt(MockEvent(start=datetime(year=self.cur.year, month=1, day=2, hour=16), end=datetime(year=self.cur.year, month=1, day=3, hour=18))),
            '2nd January 16:00 – 3rd January 18:00'
        )

    # def test_dateformat_start_end(self):
    #     self.assertEqual(
    #         self._fmt(MockEvent(start=datetime(year=self.cur.year, month=1, day=1), end=datetime(year=self.cur.year, month=1, day=2), whole_day=True)),
    #         '1st-2nd January'
    #     )

    def test_dateformat_next_year(self):
        self.assertEqual(
            self._fmt(MockEvent(start=datetime(year=self.cur.year + 1, month=1, day=2), whole_day=True)),
            '2nd January ' + str(self.cur.year + 1)
        )

    def test_dateformat_past_year(self):
        self.assertEqual(
            self._fmt(MockEvent(start=datetime(year=self.cur.year - 1, month=1, day=2), whole_day=True)),
            '2nd January ' + str(self.cur.year - 1)
        )

    def test_localized_de(self):
        translation.activate('de-DE')
        self.assertEqual(
            self._fmt_loca(MockEvent(start=datetime(year=self.cur.year, month=10, day=3), whole_day=True)),
            '3. Oktober'
        )
        translation.deactivate()

    def test_localized_fr(self):
        translation.activate('fr-FR')
        self.assertEqual(
            self._fmt_loca(MockEvent(start=datetime(year=self.cur.year, month=10, day=3), whole_day=True)),
            '3 Octobre'
        )
        translation.deactivate()
