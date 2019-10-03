from django import template

register = template.Library()


@register.tag()
def tabless(parser, token):
    nodelist = parser.parse(('endtabless', ))
    parser.delete_first_token()
    return Tabless(nodelist)


class Tabless(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        output = self.nodelist.render(context)
        return output.replace("\t", "").replace("\n", "")
