from django.shortcuts import render, get_object_or_404
from django.http import Http404, JsonResponse
from django.views.generic.list import ListView
from django.contrib.auth.models import User
from .models import Notification
import json

class NotificationList(ListView):
    template_name = "notifications/notifications_list.html"
    model = Notification
    context_object_name = 'obj'

    def get_context_data(self, **kwargs):
        context = super(NotificationList,self).get_context_data(**kwargs)
        context['notification_ids'] = list(self.request.user.notifications.filter(read=False).values_list('id', flat=True))

        return context

    def get_queryset(self):
        return self.request.user.notifications.filter(read=False)

def mark_as_read(request, pk):
    notification_ids = json.load(request)['notification_ids']
    json_response = {'success': False}
    json_response['data'] = notification_ids

    if request.user.is_authenticated:
        if notification_ids:
            Notification.objects.filter(user=request.user).filter(id__in=notification_ids).update(read=True)
            json_response['success'] = True     
    else:
        raise "User is not authenticated"

    return JsonResponse(json_response)

def check(request):
    json_response = {'success': False}
    notifications = json.load(request)['notifications']

    if request.user.is_authenticated:
        current_notifications = request.user.notifications.filter(read=False).count()
        json_response['success'] = True
        json_response['update'] = (current_notifications!=notifications)
        json_response['notifications'] = current_notifications
    else:
        raise "User is not authenticated"

    return JsonResponse(json_response)