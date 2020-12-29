from django.dispatch import Signal
from .models import Post

add_view = Signal(providing_args=["user", "post"])

def add_view_handler(sender, **kwargs):
    user = kwargs['user']
    post = kwargs['post']
    if user!=post.author:
        post.views += 1
        post.save()    

add_view.connect(add_view_handler, sender=Post)