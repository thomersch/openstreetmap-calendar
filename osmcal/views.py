import json
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import login as dj_login
from django.contrib.auth import logout as dj_logout
from django.contrib.auth.decorators import login_required
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.syndication.views import Feed
from django.db import transaction
from django.db.models import F, Q
from django.db.models.expressions import Func
from django.db.models.fields import DateTimeField
from django.forms import formset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.base import TemplateView
from pytz import UTC
from requests_oauthlib import OAuth1Session

from . import forms, osmuser
from .ical import encode_event, encode_events
from .models import (Event, EventLog, EventParticipation, ParticipationAnswer,
                     ParticipationQuestion, ParticipationQuestionChoice, User)


class LocalDateTime(Func):
    template = '%(expressions)s'
    arg_joiner = ' AT TIME ZONE '
    arity = 2

    output_field = DateTimeField()


class EventListView(View):
    def filter_queryset(self, qs, **kwargs):
        return qs.filter(
            Q(start__gte=kwargs['after']) | Q(end__gte=kwargs['after'])
        ).order_by('local_start')

    def get_queryset(self, params, after=None):
        if after is None:
            after = timezone.now()

        upcoming_events = self.filter_queryset(
            Event.objects.all().annotate(
                local_start=LocalDateTime(F('start'), F('timezone'))
            ), after=after
        )

        filter_to_country = params.get('in', None)
        if filter_to_country and len(filter_to_country) == 2:
            upcoming_events = upcoming_events.filter(location_address__country_code=filter_to_country.lower())
        elif filter_to_country:
            upcoming_events = upcoming_events.filter(location_address__country=filter_to_country)

        filter_around = params.get('around', None)
        if filter_around:
            filter_around = [float(x) for x in filter_around.split(',')]
            pt = Point(filter_around[1], filter_around[0], srid=4326)
            upcoming_events = upcoming_events.annotate(distance=Distance('location', pt)).filter(distance__lte=50000)  # distance in meter

        return upcoming_events


class Homepage(EventListView):
    def get(self, request, *args, **kwargs):
        upcoming_events = self.get_queryset(request.GET)

        country_list = Event.objects.order_by('location_address__country').filter(location_address__country__isnull=False).values_list('location_address__country', flat=True).distinct()

        return render(
            request,
            'osmcal/homepage.html',
            context={
                'user': request.user,
                'events': upcoming_events,
                'country_list': country_list,
                'filter': {
                    'in': request.GET.get('in', None),
                    'around': request.GET.get('around', None)
                }
            })


class SubscriptionInfo(TemplateView):
    template_name = 'osmcal/subscription_info.html'


class PastEvents(EventListView):
    PAGESIZE = 20

    def filter_queryset(self, qs, **kwargs):
        return qs.filter(start__lte=timezone.now()).order_by('-local_start')

    def get(self, request, page=1, **kwargs):
        evts = self.get_queryset(request.GET)
        has_more = False
        if evts.count() > page * self.PAGESIZE:
            has_more = True

        return render(request, 'osmcal/events_past.html', context={
            'page': page,
            'events': evts[self.PAGESIZE * (page - 1):self.PAGESIZE * page],
            'has_more': has_more
        })


class EventFeed(Feed, EventListView):
    title = 'OpenStreetMap Events'
    link = '/events.rss'
    description_template = 'osmcal/feeds/event_feed.html'

    def get_object(self, request, **kwargs):
        return self.get_queryset(request.GET)

    def items(self, obj):
        return obj

    def item_title(self, item):
        return item.name

    def item_link(self, item):
        return reverse('event', kwargs={'event_id': item.id})

    def item_guid(self, obj):
        return 'osmcal-event-{}'.format(obj.id)


def event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    authors = event.log.all().distinct('created_by')

    user_is_joining = False
    if not request.user.is_anonymous:
        user_is_joining = event.participation.filter(user=request.user).exists()

    return render(request, 'osmcal/event.html', context={'event': event, 'user_is_joining': user_is_joining, 'authors': authors})


class EventParticipants(TemplateView):
    template_name = 'osmcal/event_participants.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_id = kwargs['event_id']
        # TODO: validate event_id
        context['event'] = Event.objects.get(id=event_id)
        if context['event'].questions.count() > 0:
            # The following monstrosity will convert the answers into a table:
            context['answers'] = User.objects.raw('''
            SELECT
                u.id,
                u.name AS user_name,
                q.question_text AS question_text,
                e.added_on AS added_on,
                COALESCE(c.text, a.answer) AS answer
            FROM
                osmcal_user AS u
            JOIN osmcal_eventparticipation as e ON e.user_id = u.id
            LEFT JOIN osmcal_participationquestion as q ON q.event_id = e.event_id
            LEFT JOIN osmcal_participationanswer as a ON (a.question_id = q.id AND a.user_id = e.user_id)
            LEFT JOIN osmcal_participationquestionchoice as c ON (
                c.question_id = q.id AND
                q.answer_type = 'CHOI' AND
                CASE WHEN a.answer::int = c.id THEN true ELSE false END
            )
            WHERE e.event_id = %s
            ORDER BY e.id, a.user_id, q.id''', (event_id, ))
        return context


class JoinEvent(View):
    def survey(self, request, evt):
        question_form = forms.QuestionnaireForm
        return render(request, 'osmcal/event_survey.html', context={
            'event': evt,
            'form': question_form(evt.questions.all())
        })

    @method_decorator(login_required)
    def get(self, request, event_id):
        evt = Event.objects.get(id=event_id)
        if evt.questions.count() > 0:
            return self.survey(request, evt)

        return render(request, 'osmcal/event_join.html', context={'event': evt})

    @method_decorator(login_required)
    def post(self, request, event_id):
        evt = Event.objects.get(id=event_id)
        questions = evt.questions.all()
        answers = None

        if questions:
            if request.POST.get('signup-answers'):
                question_form = forms.QuestionnaireForm
                form = question_form(questions, data=request.POST)
                form.is_valid()
                answers = form.cleaned_data
            else:
                return self.survey(request, evt)

        ep = EventParticipation.objects.create(event=evt, user=request.user)
        if answers:
            for qid, answer in answers.items():
                ParticipationAnswer.objects.update_or_create(
                    question_id=qid,
                    user=request.user,
                    defaults={'answer': answer},
                )
        ep.save()
        return redirect(reverse('event', kwargs={'event_id': event_id}))


class UnjoinEvent(View):
    @method_decorator(login_required)
    def post(self, request, event_id):
        EventParticipation.objects.get(event__id=event_id, user=request.user).delete()
        # TODO: Remove ParticipationAnswers
        return redirect(reverse('event', kwargs={'event_id': event_id}))


def login(request):
    return render(request, 'osmcal/login.html', context={'next': request.GET.get('next', None)})


def logout(request):
    dj_logout(request)
    return redirect("/")


class CancelEvent(View):
    @method_decorator(login_required)
    def post(self, request, event_id=None):
        event = get_object_or_404(Event, id=event_id)

        # We don't need an event form as such, but we will use the to_json method
        # to be able to save the current data as a log entry.
        event_form = forms.EventForm(request.POST)
        event_form.is_valid()
        EventLog.objects.create(created_by=request.user, event=event, data=event_form.to_json())

        event.cancelled = True
        event.save()
        return redirect(reverse('event', kwargs={'event_id': event_id}))


class EditEvent(View):
    def _question_formset(self, request):
        QuestionFormSet = formset_factory(forms.QuestionForm)
        question_formset = QuestionFormSet(request.POST, prefix='questions')
        return question_formset

    def _questions_json(self, questions):
        q = []
        for question in questions:
            q.append({
                "text": question.question_text,
                "type": question.answer_type,
                "mandatory": question.mandatory,
                "choices": [{"text": x.text} for x in question.choices.all()],
                "frozen": True
            })
        return json.dumps(q)

    def _save_question_data(self, evt, qd):
        choices = qd.pop('choices', [])
        pq = ParticipationQuestion.objects.create(**qd)
        pq.event = evt
        for choice in choices:
            ParticipationQuestionChoice.objects.create(text=choice, question=pq)
        pq.save()

    def render(self, request, ctx):
        ctx['debug'] = settings.DEBUG
        # For existing events, we need to consider the local timezone,
        # otherwise we're just using UTC and converting it later.
        try:
            ctx['tz'] = ctx['event'].timezone
        except (AttributeError, KeyError):
            ctx['tz'] = UTC
        return render(request, 'osmcal/event_form.html', ctx)

    @method_decorator(login_required)
    def get(self, request, event_id=None):
        form = forms.EventForm()
        questions = []
        question_formset = None
        evt = None
        if event_id is not None:
            evt = Event.objects.get(id=event_id)
            questions = evt.questions.all()
            form = forms.EventForm(instance=evt)
            question_formset = self._question_formset(request)
        return self.render(request, {'form': form, 'question_formset': question_formset, 'questions': self._questions_json(questions), 'event': evt})

    @method_decorator(login_required)
    @transaction.atomic
    def post(self, request, event_id=None):
        form = forms.EventForm(request.POST)
        question_formset = self._question_formset(request)

        if event_id is not None:
            form = forms.EventForm(request.POST, instance=Event.objects.get(id=event_id))

        if form.is_valid():
            questions_data = []
            question_formset.is_valid()
            for qf in question_formset:
                questions_data.append(qf.cleaned_data)

            if event_id is None:
                evt = Event.objects.create(**form.cleaned_data)
                evt.created_by = request.user
                evt.save()
                EventLog.objects.create(created_by=request.user, event=evt, data=form.to_json())

                for qd in questions_data:
                    self._save_question_data(evt, qd)
            else:
                evt = Event.objects.get(id=event_id)
                new_questions = questions_data[question_formset.initial_form_count():]
                for question in new_questions:
                    self._save_question_data(evt, question)
                form.save()
                EventLog.objects.create(created_by=request.user, event_id=event_id, data=form.to_json())

            return redirect(reverse('event', kwargs={'event_id': event_id or evt.id}))

        return self.render(request, {'form': form, 'question_formset': question_formset})


class DuplicateEvent(EditEvent):
    def dict_from_event(self, evt, fields):
        d = {}
        for field in fields:
            d[field] = getattr(evt, field)
        return d

    @method_decorator(login_required)
    def post(self, request, event_id):
        """we are stopping event_id from propagating,
        so the existing event won't be overwritten"""
        return super().post(request)

    @method_decorator(login_required)
    def get(self, request, event_id):
        old_evt = Event.objects.get(id=event_id)

        form_data = self.dict_from_event(old_evt, ('name', 'whole_day', 'link', 'kind', 'location_name', 'location', 'description', 'timezone'))
        form_data['start'] = datetime.now().replace(
            hour=old_evt.start_localized.hour,
            minute=old_evt.start_localized.minute,
        )
        form = forms.EventForm(initial=form_data)
        form.cleaned_data = {}
        form.add_error('start', 'please set')
        if old_evt.end:
            form.add_error('end', 'please set')
        return self.render(request, {'form': form, 'page_title': 'New Event'})


class EventICal(View):
    def get(self, request, event_id):
        evt = Event.objects.get(id=event_id)
        return HttpResponse(encode_event(evt), content_type='text/calendar')


class EventFeedICal(EventListView):
    def get(self, request):
        evts = self.get_queryset(request.GET, after=timezone.now() - timedelta(days=30))
        return HttpResponse(encode_events(evts), content_type='text/calendar')


def oauth_start(request):
    osm = OAuth1Session(
        settings.OAUTH_OPENSTREETMAP_KEY,
        client_secret=settings.OAUTH_OPENSTREETMAP_SECRET
    )
    req_token = osm.fetch_request_token('https://www.openstreetmap.org/oauth/request_token')
    request.session['oauth_params'] = req_token
    if request.GET.get('next', None):
        request.session['next'] = request.GET['next']
    auth_url = osm.authorization_url('https://www.openstreetmap.org/oauth/authorize')
    return redirect(auth_url)


def oauth_callback(request):
    osm = OAuth1Session(
        settings.OAUTH_OPENSTREETMAP_KEY,
        client_secret=settings.OAUTH_OPENSTREETMAP_SECRET,
        resource_owner_key=request.session.get("oauth_params")["oauth_token"],
        resource_owner_secret=request.session.get("oauth_params")["oauth_token_secret"],
        verifier='OSMNOPE'
    )
    osm_attrs = osmuser.get_user_attributes(osm)

    try:
        u = User.objects.get(osm_id=osm_attrs['osm_id'])
    except User.DoesNotExist:
        u = User.objects.create(osm_id=osm_attrs['osm_id'])
    
    u.name = osm_attrs['display_name']
    u.home_location = osm_attrs.get('home_location', None)
    u.save()

    dj_login(request, u)
    request.session.delete("oauth_params")

    next_redir = request.session.pop('next', None)
    if next_redir:
        return redirect(next_redir)
    return redirect('/login/')


class Documentation(TemplateView):
    template_name = 'osmcal/documentation.html'


class CurrentUserView(TemplateView):
    template_name = 'osmcal/user_self.html'

    @method_decorator(login_required)
    def get(self, request):
        return super().get(self, request)
