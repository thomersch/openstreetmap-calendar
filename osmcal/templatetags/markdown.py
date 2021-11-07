import bleach
import markdown as md
from bleach.linkifier import LinkifyFilter
from django import template

allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'li', 'ol', 'p', 'pre', 'strong', 'ul']

register = template.Library()
cleaner = bleach.Cleaner(tags=allowed_tags, filters=[LinkifyFilter])


@register.filter(is_safe=True)
def markdown(value):
    if not value:
        return ""
    return cleaner.clean(md.markdown(value))


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
        return cleaner.clean(markdown(output))
