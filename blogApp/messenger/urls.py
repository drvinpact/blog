from django.urls import path
from .views import Messenger, thread, add_message, start_thread, check_updates

urlpatterns = [
    path('', Messenger.as_view(), name='messenger'),
    # path('thread/<int:pk>/', ThreadDetail.as_view(), name='detail'),
    path('thread/add', add_message, name='add'),
    path('thread/start/<username>/', start_thread, name='start'),

    path('thread/check-updates', check_updates, name='check-updates'),
    path('thread/', thread, name='thread'),
]