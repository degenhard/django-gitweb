import re
from django import template
from gravatar import get_gravatar


register = template.Library()

mailfilter = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}')


@register.simple_tag
def get_gravatar_for_author(author, size = None, rating = None):
    email = mailfilter.findall(author)
    if len(email) is 0 or len(email) > 1:
        return None
    else:
        return get_gravatar(email[0], size, rating)