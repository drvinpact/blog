from django.urls import path
from .views import Messenger, thread, add_message, start_thread, new_thread, check_updates

urlpatterns = [
    path('', Messenger.as_view(), name='messenger'),
    path('thread/add', add_message, name='add'),
    path('thread/start-thread/', start_thread, name='start_thread'),
    path('thread/new-thread/', new_thread, name='new_thread'),

    path('thread/check-updates', check_updates, name='check-updates'),
    path('thread/', thread, name='thread'),
]