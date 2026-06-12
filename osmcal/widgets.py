import babel.dates
import pytz
from django.forms.widgets import Widget
from leaflet.forms.widgets import LeafletWidget as StockLeafletWidget

# TimezoneField.to_python (forms.py) runs values through this same babel
# lookup, which normalizes "UTC" to this name. It isn't part of
# pytz.common_timezones, so it wouldn't match any <option> below.
_BABEL_UTC_NAME = babel.dates.get_timezone_name(pytz.UTC, return_zone=True)


class TimezoneWidget(Widget):
    template_name = "osmcal/partials/event_form_timezone.html"

    def format_value(self, value):
        value = super().format_value(value)
        if value == _BABEL_UTC_NAME:
            value = pytz.UTC.zone
        return value

    def get_context(self, *args, **kwargs):
        ctx = super().get_context(*args, **kwargs)
        ctx["all_timezones"] = pytz.common_timezones
        return ctx


class LeafletWidget(StockLeafletWidget):
    template_name = "osmcal/partials/leaflet_widget.html"
