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


class QuestionnaireForm(forms.Form):
    def __init__(self, questions, **kwargs):
        self.fields = {}
        super().__init__(**kwargs)
        for question in questions:
            if question.answer_type == 'TEXT':
                f = forms.CharField(label=question.question_text)
            elif question.answer_type == 'BOOL':
                f = forms.BooleanField(label=question.question_text)
            elif question.answer_type == 'CHOI':
                f = forms.ChoiceField(label=question.question_text, choices=[(x['text'], x['text']) for x in question.choices])
            else:
                raise ValueError("invalid answer_type: %s" % (question.answer_type))

            self.fields[str(question.id)] = f


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
