import json

from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.forms.widgets import DateTimeInput, TextInput
from leaflet.forms.widgets import LeafletWidget

from . import models
from .serializers import JSONEncoder


class QuestionForm(forms.ModelForm):
    choices = SimpleArrayField(forms.CharField())

    def clean_choices(self):
        return [{'text': x} for x in self.cleaned_data['choices'][0].splitlines()]

    class Meta:
        model = models.ParticipationQuestion
        fields = ('question_text', 'answer_type', 'mandatory')


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

    def to_json(self):
        d = {}
        for field in self.fields:
            d[field] = self.cleaned_data[field]

        return json.loads(json.dumps(d, cls=JSONEncoder))  # This is bad and I should feel bad.
