from datetime import datetime, tzinfo

from babel.core import Locale
from babel.dates import (format_interval, format_skeleton, get_timezone,
                         get_timezone_name)
from django import template
from django.utils.translation import gettext

register = template.Library()


@register.simple_tag()
def loca_day_month_fmt(lang):
    fmt_str = gettext('day_month_format')
    if fmt_str == 'PLACEHOLDER':
        """We're hacking around the fallback language here:
            jS F would be 1st May in en, but in everything else we'd have 1st Май, which doesn't make any sense, so we have a placeholder in the translation and going to fallback to j E which is reasonable in most languages."""
        if lang.startswith('en'):
            return 'jS F'
        else:
            return 'j E'
    return fmt_str


@register.simple_tag()
def loca_day_fmt(lang):
    fmt_str = gettext('day_only_format')
    if fmt_str == 'PLACEHOLDER':
        if lang.startswith('en'):
            return 'jS'
        else:
            return 'j'
    return fmt_str


DEFAULT_LOCALE = 'en_GB'


def with_timezone(original, evt, locale,
                  user_tz: tzinfo = None):
    """
        The timezone concatenation might be incorrect in some cases, but there
        seems not to be a format string for this purpose.
    """
    dt = evt.start_localized
    if user_tz:
        dt = evt.start.astimezone(user_tz)

    """
        This is just a hack to prevent an ugly display like "Unknown Region
        (GMT) Time". It should be replaced with something better.
    """
    if dt.tzname() == 'GMT':
        return original + ' GMT'
    elif dt.tzname() == 'UTC':
        return original + ' UTC'

    return original + ' ' + get_timezone_name(
        dt.tzinfo, width='short', locale=locale
    )


@register.simple_tag()
def full_date_format(evt, locale=DEFAULT_LOCALE,
                     user_tz: tzinfo = None) -> str:
    """
        full_date_format formats the date/time of an event.
        There are several things to keep in mind:
        - Events always have a start, but not always a specified end.
        - They might be just a range of dates (whole_day).
        - Events are located in some timezone.
        - If the consumer is in a different timezone than the event, it should
          be converted.
            - If the event is a whole day event, timezone should not be
              converted as this would bring dates out of alignment.
        - They should be displayed in a localized, but concise fashion, without
          unnecessary repetition.
    """
    lo = Locale.parse(locale, sep='_')
    tz = get_timezone(evt.timezone)

    if evt.end:
        if evt.whole_day:
            return format_interval(
                evt.start.date(), evt.end.date(), 'yMMMMd',
                tzinfo=tz, locale=lo
            )
        else:
            if evt.start.date() == evt.end.date():
                fmt = lo.datetime_formats['medium'].replace("'", "")
                return with_timezone(fmt.format(
                    format_interval(evt.start.time(), evt.end.time(),
                                    'Hm', tzinfo=tz, locale=lo),
                    format_skeleton('yMMMMd', evt.start,
                                    tzinfo=tz, locale=lo)
                ), evt, lo, user_tz)
            return with_timezone(
                format_interval(evt.start, evt.end, skeleton='yMMMMd Hm',
                                tzinfo=tz, locale=lo),
                evt, lo, user_tz
            )

    # Event has no end date
    if evt.whole_day:
        return format_skeleton('yMMMMd', evt.start, tzinfo=tz, locale=lo)
    else:
        fmt = lo.datetime_formats['medium'].replace("'", "")
        return with_timezone(fmt.format(
            format_skeleton('Hm', evt.start, tzinfo=tz, locale=lo),
            format_skeleton('yMMMMd', evt.start, tzinfo=tz, locale=lo)
        ), evt, lo, user_tz)


@register.simple_tag()
def short_date_format(evt, locale=DEFAULT_LOCALE,
                      user_tz: tzinfo = None) -> str:
    lo = Locale.parse(locale, sep='_')
    tz = get_timezone(evt.timezone)
    now = datetime.now()

    if evt.end:
        if evt.start.year != now.year or evt.end.year != evt.start.year:
            return format_interval(
                evt.start.date(), evt.end.date(), 'yMMMMd',
                tzinfo=tz, locale=lo
            )
        else:
            # Year can be skipped
            return format_interval(
                evt.start.date(), evt.end.date(), 'MMMd',
                tzinfo=tz, locale=lo
            )

    if evt.start.year != now.year:
        return format_skeleton('yMMMMd', evt.start, tzinfo=tz, locale=lo)
    else:
        # Year can be skipped
        return format_skeleton('MMMMd', evt.start, tzinfo=tz, locale=lo)
