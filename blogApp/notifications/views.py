from django.shortcuts import render, get_object_or_404
from django.views.generic.list import ListView
from django.contrib.auth.models import User
from .models import Notification

class NotificationList(ListView):
    template_name = "notifications/notifications_list.html"
    model = Notification
    context_object_name = 'obj'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user)
        return Notification.objects.filter(user=user)