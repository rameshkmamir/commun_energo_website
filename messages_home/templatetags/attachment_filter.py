import imghdr

from django import template

register = template.Library()


@register.filter
def is_image(attachment):
    try:
        return imghdr.what(attachment.file) is not None
    except:
        return False


@register.filter
def replace(value, arg):
    return value.replace(arg, '')
