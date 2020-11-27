from django.shortcuts import render, get_object_or_404
from django.http import Http404, JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from .models import Notification
import json

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string


@method_decorator(login_required, name='dispatch')
class NotificationList(TemplateView):
    template_name = "notifications/notification_list.html"

    def get_context_data(self, **kwargs):
        context = super(NotificationList,self).get_context_data(**kwargs)
        notifications = self.request.user.notifications.filter(read=False)
        html = render_to_string('notifications/partials/notification_list.html', {'notifications': notifications[:15]})
        context['notifications'] = html
        notifications.update(read=True)

        return context

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