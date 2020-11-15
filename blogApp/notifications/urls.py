from django.urls import path
from .views import NotificationList, mark_as_read, check

urlpatterns = [
    path('', NotificationList.as_view(), name='list'),    
    path('mark_as_read/<int:pk>', mark_as_read, name='mark_as_read'),    
    path('check', check, name='check'),    
]