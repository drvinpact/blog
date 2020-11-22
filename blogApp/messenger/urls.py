from django.urls import path
from .views import ThreadList, ThreadDetail, add_message, start_thread, check_updates, ThreadListt, ThreadDetaill

urlpatterns = [
    path('', ThreadList.as_view(), name='list'),
    path('thread/<int:pk>/', ThreadDetail.as_view(), name='detail'),
    path('thread/<int:pk>/add', add_message, name='add'),
    path('thread/start/<username>/', start_thread, name='start'),
    
    path('threadd/', ThreadListt.as_view(), name='listt'),
    path('threadd/<int:pk>/', ThreadDetaill.as_view(), name='detaill'),

    path('thread/check-updates', check_updates, name='check-updates'),
]