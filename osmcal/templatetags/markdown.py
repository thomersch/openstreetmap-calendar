from django import template

import markdown2


register = template.Library()


@register.filter(is_safe=True)
def markdown(value):
    if not value:
        return ""
    return markdown2.markdown(value, safe_mode=True)


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
        return markdown2.markdown(output, safe_mode=True)
