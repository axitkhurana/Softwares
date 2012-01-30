from django import template
register = template.Library()

@register.filter
def hash(h,key):
    if key in h.keys():
        return h[key]
    else:
        return None
