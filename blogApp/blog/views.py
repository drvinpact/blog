from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment, Vote, Bookmark
from .forms import CommentForm, ReplyForm
from django import forms
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class BaseListView(ListView):
    template_name = 'blog/home.html'
    model = Post
    context_object_name = 'obj'
    ordering = ['-created_at']
    paginate_by = 10

class PostListView(BaseListView):
    def get_queryset(self):
        search = self.request.GET.get('search')
        if search and search is not None:
            return Post.objects.filter(
                Q(title__contains=search.strip()) | 
                Q(content__contains=search.strip())
            ).distinct().order_by('-created_at')

        return Post.objects.all().order_by('-created_at')

class PostsByCategory(BaseListView):
    def get_queryset(self):
        return Post.objects.filter(category__name=self.kwargs.get('category')).order_by('-created_at')
 
class PostsByTag(BaseListView):
    def get_queryset(self):
        return Post.objects.filter(tags__name__in=[self.kwargs.get('tag')]).order_by('-created_at')

class PostsByDate(BaseListView):
    def get_queryset(self):
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')            
        return Post.objects.filter(created_at__year=year).filter(created_at__month=month).order_by('-created_at')

class UserPostListView(BaseListView):
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-created_at')

@method_decorator(login_required, name='dispatch')
class BookmarkPostListView(BaseListView):
    def get_queryset(self):        
        bookmarks_ids = list(self.request.user.bookmarks.values_list('post_id', flat=True))
        return Post.objects.filter(pk__in=bookmarks_ids).order_by('-created_at')

@method_decorator(login_required, name='dispatch')
class MyPostListView(BaseListView):
    def get_queryset(self):        
        return self.request.user.posts.all().order_by('-created_at')

class PostDetailView(DetailView):
    def get(self, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs.get('pk'))
        comments = post.comments.filter(active=True, parent=None).order_by('-created_at')
        form = CommentForm()

        if self.request.user.is_authenticated:
            form.fields['name'].widget = forms.HiddenInput()
            form.fields['email'].widget = forms.HiddenInput()
            form.fields['website'].widget = forms.HiddenInput()
            form.fields['content'].label = ''

        context = {'post': post, 'comments': comments, 'form': form}
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
class UserView(DetailView):
    slug_field = "username"
    model = User
    template_name = 'blog/user_profile.html'
    context_object_name = 'obj'

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

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
    template_name = 'blog/post_confirm_deactivate.html'
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        if self.object.author == self.request.user:
            self.object.active=(not self.object.active)
            self.object.save()

        return redirect(success_url)
 
def about(request):
    template_name = 'blog/about.html'
    return render(request, template_name, {'title': 'About'})

def contact(request):
    template_name = 'blog/contact.html'
    return render(request, template_name, {'title': 'Contact'})

""" AJAX """

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
                post = Post.objects.get(pk=pk)
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
            post = Post.objects.get(pk=pk)
            marker = Bookmark.objects.create_or_delete(user=request.user, post=post)
            bookmark = True if marker else False
            
            return JsonResponse({ 'success': True, 'bookmark': bookmark }, safe=False)
        except ObjectDoesNotExist:
            return JsonResponse({'msg': 'The object does not exist', 'success': False}, safe=False)