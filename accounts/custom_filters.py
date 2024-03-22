from django import template

register = template.Library()

@register.filter(name='addcss')
def addcss(value, arg):
    """
    Adds the specified CSS class(es) to the HTML element.
    """
    css_classes = value.field.widget.attrs.get('class', '')
    if css_classes:
        css_classes = css_classes.split(' ')
    else:
        css_classes = []
    css_classes += arg.split()
    value.field.widget.attrs['class'] = ' '.join(css_classes)
    return value