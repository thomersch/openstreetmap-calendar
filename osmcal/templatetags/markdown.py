import bleach
import markdown as md
from django import template

allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'i', 'li', 'ol', 'p', 'strong', 'ul']

register = template.Library()


@register.filter(is_safe=True)
def markdown(value):
    if not value:
        return ""
    return bleach.clean(md.markdown(value), tags=allowed_tags)


@register.tag()
def markdownify(parser, token):
    nodelist = parser.parse(('endmarkdownify', ))
    parser.delete_first_token()
    return Markdownify(nodelist)


class Markdownify(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        output = self.nodelist.render(context)
        return bleach.clean(md.markdown(output), tags=allowed_tags)
