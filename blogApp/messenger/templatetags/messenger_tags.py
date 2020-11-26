from django import template

register = template.Library()

@register.simple_tag
def get_unread_count(thread, user):
    if thread:
        return thread.messages.filter(read=False).exclude(user=user).count()
    return 0