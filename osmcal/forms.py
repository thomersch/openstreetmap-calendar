from django import forms
from django.forms.widgets import DateTimeInput, TextInput
from leaflet.forms.widgets import LeafletWidget

from . import models


class EventForm(forms.ModelForm):
    class Meta:
        model = models.Event
        fields = ('name', 'whole_day', 'start', 'end', 'link', 'kind', 'location_name', 'location', 'description')
        widgets = {
            'location': LeafletWidget(),
            'start': DateTimeInput(attrs={'class': 'datepicker-flat'}),
            'end': DateTimeInput(attrs={'class': 'datepicker-flat', 'placeholder': 'optional'}),
            'link': TextInput(attrs={'placeholder': 'https://'}),
            'location_name': TextInput(attrs={'placeholder': 'e.g. Café International'})
        }
