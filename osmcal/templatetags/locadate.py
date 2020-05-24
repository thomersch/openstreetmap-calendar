from django import template
from django.utils.translation import check_for_language, gettext

register = template.Library()

@register.simple_tag()
def loca_day_fmt(lang):
    fmt_str = gettext('day_month_format')
    if fmt_str == 'PLACEHOLDER':
        """We're hacking around the fallback language here:
            jS F would be 1st May in en, but in everything else we'd have 1st Май, which doesn't make any sense, so we have a placeholder in the translation and going to fallback to j E which is reasonable in most languages."""
        if lang.startswith('en'):
            return 'jS F'
        else:
            return 'j E'
    return fmt_str
