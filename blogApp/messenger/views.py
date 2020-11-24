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
from django.db.models import F, Max, Count, Sum
from django.db.models.functions import Concat
from django.db.models import CharField, Value, Subquery, OuterRef

from django.template.loader import render_to_string
import json


@method_decorator(login_required, name="dispatch")
class Messenger(TemplateView):
    template_name = "messenger/messenger.html"

    def get_context_data(self, **kwargs):
        context = super(Messenger, self).get_context_data(**kwargs)        
        context['last_update'] = Thread.objects.thread_last_update(self.request.user)

        return context

        
@method_decorator(login_required, name="dispatch")
class ThreadDetail(DetailView):
    model = Thread

    def get_object(self):
        obj = super(ThreadDetail, self).get_object()
        if self.request.user not in obj.users.all():
            raise PermissionDenied()
        
        return obj

def add_message(request):
    json_response = {'created':False}
    if request.user.is_authenticated:
        data = json.loads(request.body.decode("utf-8"))    
        thread_id = data['thread_id']
        content = data['content']
        if content:
            thread = get_object_or_404(Thread, pk=thread_id)
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
    json_response = {'update': False, 'update_list': False}
    if request.user.is_authenticated:
        data = json.loads(request.body.decode("utf-8"))
        thread_id = data['thread_id']
        last_update = data['last_update']

        last_thread = Thread.objects.last_thread(request.user)

        if last_thread:
            current_last_update = format(last_thread.updated_at, 'U')        
            json_response['current_last_update'] = current_last_update
            json_response['last_update'] = last_update

            if last_update!=current_last_update:
                json_response['update_list'] = True
                html_list = render_to_string('messenger/partials/thread_list.html', {'user': request.user, 'last_update': current_last_update})
                json_response['html_list'] = html_list
                json_response['thread_id'] = thread_id
                json_response['last_thread_id'] = last_thread.id

                if thread_id and thread_id==last_thread.id:
                    # thread = get_object_or_404(Thread, pk=thread_id)
                    # last_update = format(thread.updated_at, 'U')                    
                    json_response['update'] = True
                    html = render_to_string('messenger/partials/thread_messages.html', {'thread': last_thread, 'user': request.user})
                    json_response['html'] = html
            # subquery = Message.objects.filter(thread=OuterRef('pk')).order_by('-pk')[:1]
            # threads = Thread.objects.filter(
            #                             messages__id=Subquery(subquery.values('pk'))
            #                         ).annotate(
            #                             content=F('messages__content'),
            #                             created_at=F('messages__created_at')
            #                         ).values('id', 'created_at', 'content')

            # json_response['threads'] = list(threads)
                        
    else:
        raise "User is not authenticated"

    return JsonResponse(json_response)

def thread(request):
    json_response = {'update': False}
    if request.user.is_authenticated:
        data = json.loads(request.body.decode("utf-8"))
        thread_id = data['thread_id']
        thread = get_object_or_404(Thread, pk=thread_id)
        json_response['update'] = True
        html = render_to_string('messenger/partials/thread_messages.html', {'thread': thread, 'user': request.user})
        json_response['html'] = html
    else:
        raise "User is not authenticated"

    return JsonResponse(json_response)

@login_required
def start_thread(request, username):
    user = get_object_or_404(User, username=username)
    thread = Thread.objects.find_or_create(user, request.user)

    return redirect(reverse_lazy('messenger:detail', args=[thread.pk])) 
