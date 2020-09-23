from django.forms.widgets import Widget
from leaflet.forms.widgets import LeafletWidget as StockLeafletWidget


class TimezoneWidget(Widget):
    template_name = 'osmcal/partials/event_form_timezone.html'


class LeafletWidget(StockLeafletWidget):
    template_name = 'osmcal/partials/leaflet_widget.html'
