from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment, Vote
from .forms import CommentForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View

def home(request):
    template_name = 'blog/home.html'
    posts = Post.objects.all()
    context = {'posts': posts}
    return render(request, template_name, context)

class PostListView(ListView):
    template_name = 'blog/home.html'
    model = Post
    context_object_name = 'obj'
    ordering = ['-created_at']
    paginate_by = 5

class UserPostListView(ListView):
    template_name = 'blog/user_posts.html'
    model = Post
    context_object_name = 'obj'    
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-created_at')

class PostDetailView(View):
    def get(self, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs.get('pk'))
        comments = post.comments.filter(active=True).order_by('-created_at')
        form = CommentForm()
        context = {'post': post, 'comments': comments, 'form': form}
        return render(self.request, "blog/post_detail.html", context)
    
    def post(self, *args, **kwargs):
        form = CommentForm(self.request.POST or None)
        if form.is_valid():
            pk = self.kwargs.get('pk')
            post = get_object_or_404(Post, pk=pk)
            content = form.cleaned_data.get("content")
            if content:
                comment = Comment(
                    content=content,
                    author=self.request.user,
                    post=post
                )
                comment.save()
                return redirect('blog:post_detail', pk=pk)
            else:
                messages.info(self.request, "Please write some comment.")
                return redirect('blog:post_detail', pk=pk)

def vote(request, pk, slug):
    if request.method=='POST':
        try:
            like = True if request.POST.get("like") is "1" else False
            if slug == 'post':
                post = Post.objects.get(pk=pk)
                vote = Vote.objects.update_or_create(post=post, defaults={
                    'author':request.user,
                    'post':post,
                    'like':like
                })
            elif slug == 'comment':
                comment = Comment.objects.get(pk=pk)
                vote = Vote.objects.update_or_create(comment=comment, defaults={
                    'author':request.user,
                    'comment':comment,
                    'like':like
                })
            
            return HttpResponse("OK")
        except ObjectDoesNotExist:
            return HttpResponse("NOTOK")

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
            
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

def about(request):
    template_name = 'blog/about.html'
    return render(request, template_name, {'title': 'About'})
