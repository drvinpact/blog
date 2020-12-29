from django import template

register = template.Library()

@register.simple_tag
def get_post_bookmark(post, user):    
    if user and post:
        return user.profile.bookmark(post)
    return False