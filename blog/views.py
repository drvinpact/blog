from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from .models import Post, Comment, Vote, Bookmark
from .forms import PostForm, CommentForm, ReplyForm
from django import forms
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .utils import api_response
import requests
import time
import json
from .constants import contact_template_slug, newsletter_template_slug, email_sender_url, email_sender_api_key

from .signals import add_view
import urllib3

class BaseListView(ListView):
    template_name = 'blog/home.html'
    model = Post
    context_object_name = 'obj'
    ordering = ['-created_at']
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        list_type = request.session.get('list_type', 0)
        context['list_type'] = list_type
        return render(self.request, 'blog/home.html', context)

    def post(self, *args, **kwargs):
        list_type = self.request.POST.get('list')
        self.request.session['list_type'] = list_type
        return redirect(reverse_lazy('blog:home'))


class PostListView(BaseListView):
    def get_queryset(self):
        search = self.request.GET.get('search')
        if search and search is not None:
            return Post.active.filter(
                Q(title__contains=search.strip()) | 
                Q(content__contains=search.strip())
            ).distinct().order_by('-created_at')

        return Post.active.all().order_by('-created_at')

class PostsByCategory(BaseListView):
    def get_queryset(self):
        return Post.active.filter(category__name=self.kwargs.get('category')).order_by('-created_at')
 
class PostsByTag(BaseListView):
    def get_queryset(self):
        return Post.active.filter(tags__name__in=[self.kwargs.get('tag')]).order_by('-created_at')

class PostsByDate(BaseListView):
    def get_queryset(self):
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')            
        return Post.active.filter(created_at__year=year).filter(created_at__month=month).order_by('-created_at')

class UserPostListView(BaseListView):
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.active.filter(author=user).order_by('-created_at')

@method_decorator(login_required, name='dispatch')
class BookmarkPostListView(BaseListView):
    def get_queryset(self):        
        bookmarks_ids = list(self.request.user.bookmarks.values_list('post_id', flat=True))
        return Post.active.filter(pk__in=bookmarks_ids).order_by('-created_at')

@method_decorator(login_required, name='dispatch')
class MyPostListView(BaseListView):
    def get_queryset(self):        
        return self.request.user.posts.filter(is_active=True).order_by('-created_at')

@method_decorator(login_required, name='dispatch')
class MyDeletedPostListView(BaseListView):
    def get_queryset(self):        
        return self.request.user.posts.filter(is_active=False).order_by('-created_at')

class PostDetailView(DetailView):
    def get(self, *args, **kwargs):
        comment_id = self.request.GET.get('comment_id')
        post = get_object_or_404(Post, pk=self.kwargs.get('pk'))        
        comments = post.comments.filter(active=True, parent=None).order_by('-created_at')
        form = CommentForm()

        if self.request.user.is_authenticated:
            form.fields['name'].widget = forms.HiddenInput()
            form.fields['email'].widget = forms.HiddenInput()
            form.fields['website'].widget = forms.HiddenInput()
            form.fields['content'].label = ''

        context = {'post': post, 'comments': comments, 'form': form, 'comment_id': comment_id}

        add_view.send(sender=Post, user=self.request.user, post=post)

        return render(self.request, "blog/post_detail.html", context)
    
    def post(self, *args, **kwargs):
        form = CommentForm(self.request.POST or None)
        if form.is_valid():
            pk = self.kwargs.get('pk')
            post = get_object_or_404(Post, pk=pk)
            name = form.cleaned_data.get("name")
            email = form.cleaned_data.get("email")
            website = form.cleaned_data.get("website")
            content = form.cleaned_data.get("content")
            parent_id = form.cleaned_data.get("parent_id")

            if content:
                if self.request.user.is_authenticated:                
                    comment = Comment(
                        content=content,
                        author=self.request.user,
                        post=post
                    )
                else:
                    comment = Comment(
                        content=content,
                        name=name,
                        email=email,
                        website=website,
                        post=post
                    )

                if parent_id:
                    parent_comment = Comment.objects.get(pk=parent_id)
                    comment.parent = parent_comment
                    
                comment.save()
                return redirect('blog:post_detail', pk=pk)
            else:
                messages.info(self.request, "Please write some comment.")
                return redirect('blog:post_detail', pk=pk)

@method_decorator(login_required, name='dispatch')
class UsersListView(ListView):
    template_name = 'blog/users.html'
    model = User
    context_object_name = 'obj'
    ordering = ['username']
    paginate_by = 12

    def get_queryset(self):
        return User.objects.filter(profile__is_public=True).exclude(pk=self.request.user.pk).order_by('username')

@method_decorator(login_required, name='dispatch')
class UserView(UserPassesTestMixin, DetailView):
    slug_field = "username"
    model = User
    template_name = 'blog/user_profile.html'
    context_object_name = 'obj'
    
    def handle_no_permission(self):
        return redirect('profile')

    def test_func(self):
        user = self.get_object()        
        if self.request.user==self.get_object():            
            return False
        if user.profile.is_public is False:
            raise Http404
        return True

    def get_context_data(self, **kwargs):
        context = super(UserView, self).get_context_data(**kwargs)
        context['posts'] = self.object.posts.filter(is_active=True).order_by('-created_at')[:4]
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    # fields = ['image', 'category', 'title', 'content', 'is_active']    
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
            
class PostDeactivateView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post

    def get(self, *args, **kwargs):
        raise Http404
    
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = '/'
        if self.object.author == self.request.user:
            self.object.is_active=(not self.object.is_active)
            self.object.save()
            success_url = '/posts' if self.object.is_active else '/deleted-posts'

        return redirect(success_url)
 
def about(request):
    template_name = 'blog/about.html'
    return render(request, template_name, {'title': 'About'})

def contact(request):
    template_name = 'blog/contact.html'
    return render(request, template_name, {'title': 'Contact'})

""" AJAX """


def send_email(request):
    json_response = {'success': False}

    http = urllib3.PoolManager()

    data = json.loads(request.body.decode("utf-8"))

    if('subject' not in data): 
        json_response['msg'] = 'El campo \'subject\' no puede estar vacío' 
        return api_response(json_response)
    elif('email' not in data): 
        json_response['msg'] = 'El campo \'email\' no puede estar vacío' 
        return api_response(json_response)
    elif('content' not in data): 
        json_response['msg'] = 'El campo \'content\' no puede estar vacío' 
        return api_response(json_response)

    name = data['name']
    email = data['email']
    subject = data['subject']
    content = data['content']

    attempt_num = 0
    while attempt_num < 1:       
        body = {'name': name, 'from': email, 'subject': subject, 'content': content, 'template_slug': contact_template_slug, 'type': 'contact'}
        headers = {'Content-Type': 'application/json', 'api-key': email_sender_api_key}
        response = http.request(
            'POST',
            email_sender_url,
            body=json.dumps(body),
            headers=headers
        )
        if response.status == 200:
            data = json.loads(response.data.decode('utf-8'))
            return JsonResponse(data)
        else:
            attempt_num += 1
            time.sleep(5) 

    json_response["msg"] = "Hubo un problema con la solicitud."

    return JsonResponse(json_response)

def subscribe_newsletter(request):
    json_response = {'success': False}

    http = urllib3.PoolManager()

    data = json.loads(request.body.decode("utf-8"))

    if('email' not in data): 
        json_response['msg'] = 'El campo \'email\' no puede estar vacío' 
        return api_response(json_response)
   
    email = data['email']    
   
    attempt_num = 0
    while attempt_num < 1:       
        body = {'from': email, 'template_slug': newsletter_template_slug, 'type': 'newsletter'}
        headers = {'Content-Type': 'application/json', 'api-key': email_sender_api_key}
        response = http.request(
            'POST',
            email_sender_url,
            body=json.dumps(body),
            headers=headers
        )
        if response.status == 200:
            data = json.loads(response.data.decode('utf-8'))
            return JsonResponse(data)
        else:
            attempt_num += 1
            time.sleep(5) 

    json_response["msg"] = "Hubo un problema con la solicitud."

    return JsonResponse(json_response)

def ajax_form(request):
    if request.method == "GET":
        form = CommentForm()
        return HttpResponse(form.as_p())

def vote(request, pk, slug):
    if request.method=='POST':
        try:            
            like = True if request.POST.get("like") == "1" else False
            votes = 0
            if slug == 'post':
                post = Post.active.get(pk=pk)
                vote = Vote.objects.update_or_create(post=post, author=request.user, defaults={
                    'author': request.user,
                    'post': post,
                    'like': like
                })
                likes = post.get_likes()
                dislikes = post.get_dislikes()
            elif slug == 'comment':
                comment = Comment.objects.get(pk=pk)
                vote = Vote.objects.update_or_create(comment=comment, author=request.user, defaults={
                    'author': request.user,
                    'comment': comment,
                    'like': like
                })
                likes = comment.get_likes()
                dislikes = comment.get_dislikes()
            
            return JsonResponse({ 'success': True, 'likes': likes, 'dislikes': dislikes }, safe=False)
        except ObjectDoesNotExist:
            return JsonResponse({ 'msg': 'The object does not exist', 'success': False }, safe=False)
        
def bookmark(request, pk):
    if request.method=='POST':
        try:
            post = Post.active.get(pk=pk)
            marker = Bookmark.objects.create_or_delete(user=request.user, post=post)
            bookmark = True if marker else False
            
            return JsonResponse({ 'success': True, 'bookmark': bookmark }, safe=False)
        except ObjectDoesNotExist:
            return JsonResponse({'msg': 'The object does not exist', 'success': False}, safe=False)