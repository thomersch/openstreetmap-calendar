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
