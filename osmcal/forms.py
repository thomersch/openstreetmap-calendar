import json
from typing import Dict, Iterable

import babel.dates
import pytz
from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.forms import ValidationError
from django.forms.widgets import DateTimeInput, TextInput

from . import models
from .serializers import JSONEncoder
from .widgets import LeafletWidget, TimezoneWidget


class TimezoneField(forms.Field):
    def to_python(self, value):
        try:
            return pytz.timezone(
                babel.dates.get_timezone_name(value, return_zone=True)
            )
        except pytz.exceptions.Error:
            return None

    def validate(self, value):
        if not value:
            raise ValidationError('no value', code='required')


class QuestionForm(forms.ModelForm):
    choices = SimpleArrayField(forms.CharField())

    def clean_choices(self):
        return [x for x in self.cleaned_data['choices'][0].splitlines() if x]

    class Meta:
        model = models.ParticipationQuestion
        fields = ('question_text', 'answer_type', 'mandatory')


class QuestionnaireForm(forms.Form):
    def __init__(self, questions: Iterable[models.ParticipationQuestion], **kwargs) -> None:
        self.fields: Dict[str, forms.Field] = {}
        super().__init__(**kwargs)
        for question in questions:
            if question.answer_type == 'TEXT':
                f = forms.CharField(label=question.question_text, required=question.mandatory)
            elif question.answer_type == 'BOOL':
                f = forms.BooleanField(label=question.question_text, required=question.mandatory)
            elif question.answer_type == 'CHOI':
                f = forms.ChoiceField(label=question.question_text, required=question.mandatory, choices=[(x.id, x.text) for x in question.choices.all()])
            else:
                raise ValueError("invalid answer_type: %s" % (question.answer_type))

            self.fields[str(question.id)] = f

    def clean(self, *args, **kwargs):
        for k, v in self.cleaned_data.items():
            self.cleaned_data[int(k)] = self.cleaned_data.pop(k)
        return super().clean()


class EventForm(forms.ModelForm):
    timezone = TimezoneField(required=True, widget=TimezoneWidget())

    class Meta:
        model = models.Event
        fields = ('name', 'whole_day', 'start', 'end', 'link', 'kind', 'location_name', 'location', 'timezone', 'description')
        widgets = {
            'location': LeafletWidget(),
            'start': DateTimeInput(attrs={'class': 'datepicker-flat'}),
            'end': DateTimeInput(attrs={'class': 'datepicker-flat', 'placeholder': 'optional'}),
            'link': TextInput(attrs={'placeholder': 'https://'}),
            'location_name': TextInput(attrs={'placeholder': 'e.g. Café International'}),
        }
        unlogged_fields = ('timezone', )

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        
        if self.errors:
            return self.cleaned_data

        tz = self.cleaned_data.get('timezone', None)

        """
        Django automatically assumes that datetimes are in the default time zone (UTC),
        but in fact they're in the local time zone, so we're stripping the tzinfo from
        the field and setting it to the given time zone.
        This does not change the value of the time itself, only the time zone placement.
        """
        self.cleaned_data['start'] = tz.localize(self.cleaned_data['start'].replace(tzinfo=None))

        if self.cleaned_data['end']:
            self.cleaned_data['end'] = tz.localize(self.cleaned_data['end'].replace(tzinfo=None))

        if self.cleaned_data['end'] <= self.cleaned_data['start']:
            self.add_error('end', 'Event end has to be after its start.')

    def to_json(self):
        d = {}
        for field in self.fields:
            if field in self.Meta.unlogged_fields:
                continue
            d[field] = self.cleaned_data[field]

        return json.loads(json.dumps(d, cls=JSONEncoder))  # This is bad and I should feel bad.
