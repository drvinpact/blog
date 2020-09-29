from django.urls import path
from . import views
from .views import PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView, UserPostListView, vote, ajax_form

urlpatterns = [
    path('', PostListView.as_view(), name='home'),
    path('vote/<int:pk>/<slug:slug>', vote, name="vote"),
    path('ajax_form/', ajax_form, name="ajax_form"),
    path('user/<str:username>/', UserPostListView.as_view(), name='user_posts'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/new/', PostCreateView.as_view(), name='post_new'),
    path('posts/<int:pk>/update/', PostUpdateView.as_view(), name='post_update'),
    path('posts/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),

    path('about/', views.about, name='about'),
]