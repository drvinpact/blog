from django.urls import path
from .views import Messenger, ThreadList, ThreadDetail, add_message, start_thread, check_updates

urlpatterns = [
    path('', ThreadList.as_view(), name='list'),
    path('messenger/', Messenger.as_view(), name='messenger'),
    path('thread/<int:pk>/', ThreadDetail.as_view(), name='detail'),
    path('thread/<int:pk>/add', add_message, name='add'),
    path('thread/start/<username>/', start_thread, name='start'),

    path('thread/check-updates', check_updates, name='check-updates'),
]