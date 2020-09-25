import pytz
from django.forms.widgets import Widget
from leaflet.forms.widgets import LeafletWidget as StockLeafletWidget


class TimezoneWidget(Widget):
    template_name = 'osmcal/partials/event_form_timezone.html'

    def get_context(self, *args, **kwargs):
        ctx = super().get_context(*args, **kwargs)
        ctx['all_timezones'] = pytz.common_timezones
        return ctx


class LeafletWidget(StockLeafletWidget):
    template_name = 'osmcal/partials/leaflet_widget.html'
