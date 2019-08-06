from django import template

import markdown2


register = template.Library()


@register.filter(is_safe=True)
def markdown(value):
    return markdown2.markdown(value, safe_mode=True)
