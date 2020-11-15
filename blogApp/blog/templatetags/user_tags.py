from django import template

register = template.Library()

@register.simple_tag
def get_notification_count(user):
    if user:
        return user.notifications.filter(read=False).count()
    return 0