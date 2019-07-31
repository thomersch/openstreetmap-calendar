from django import forms
from django.forms.widgets import DateTimeInput, TextInput
from leaflet.forms.widgets import LeafletWidget

from . import models


class EventForm(forms.ModelForm):
    class Meta:
        model = models.Event
        fields = ('name', 'start', 'end', 'whole_day', 'link', 'kind', 'location', 'description')
        widgets = {
            'location': LeafletWidget(),
            'start': DateTimeInput(attrs={'class': 'datepicker-flat'}),
            'end': DateTimeInput(attrs={'class': 'datepicker-flat'}),
            'link': TextInput(attrs={'placeholder': 'https://'})
        }
