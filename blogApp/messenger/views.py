from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from .models import Thread, Message
from django.http import Http404, JsonResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from users.mixins import AuthorCheckMixin
from django.utils.dateformat import format
from django.db.models import F

import json

@method_decorator(login_required, name="dispatch")
class ThreadList(TemplateView):
    template_name = "messenger/thread_list.html"

    """
    def get_queryset(self):
        
        queryset = super(ThreadList, self).get_queryset()
        return queryset.filter(users=self.request.user)
        """

@method_decorator(login_required, name="dispatch")
class Messenger(TemplateView):
    template_name = "messenger/messenger.html"
        
@method_decorator(login_required, name="dispatch")
class ThreadDetail(DetailView):
    model = Thread

    def get_object(self):
        obj = super(ThreadDetail, self).get_object()
        if self.request.user not in obj.users.all():
            raise PermissionDenied()
        
        return obj

def add_message(request, pk):
    json_response = {'created':False}
    if request.user.is_authenticated:
        content = request.GET.get('content', None)
        if content:
            thread = get_object_or_404(Thread, pk=pk)
            message = Message.objects.create(thread=thread, user=request.user, content=content)
            thread.save()
            json_response['created'] = True
            json_response['created_at'] = message.created_at.strftime("%b. %d, %Y, %I:%M %p")
            total = thread.messages.all().count()
            if total==1:
                json_response['first'] = True
            json_response['total'] = total
            json_response['last_update'] = format(thread.updated_at, 'U')
    else:
        raise "User is not authenticated"

    return JsonResponse(json_response)

def check_updates(request):
    json_response = {'update': False}
    if request.user.is_authenticated:
        data = json.loads(request.body.decode("utf-8"))
        thread_id = data['thread_id']
        updated_at = data['updated_at']
        thread = get_object_or_404(Thread, pk=thread_id)
        last_update = format(thread.updated_at, 'U')
        if last_update!=updated_at:
            json_response['update'] = True
            thread_list = list(thread.messages.annotate(author=F("user__username")).values())
            json_response['thread_list'] = thread_list        
            json_response['last_update'] = last_update
    else:
        raise "User is not authenticated"

    return JsonResponse(json_response)

@login_required
def start_thread(request, username):
    user = get_object_or_404(User, username=username)
    thread = Thread.objects.find_or_create(user, request.user)

    return redirect(reverse_lazy('messenger:detail', args=[thread.pk])) 
