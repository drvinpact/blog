from django import template
from blog.models import Category, Post
from django.db.models import Q, Count
from django.db.models.functions import ExtractMonth, ExtractYear, TruncDate
from django.utils.dateformat import format
from taggit.models import Tag



register = template.Library()

@register.simple_tag
def get_latest_posts():
    qs = Post.objects.order_by('-created_at')[:3]
    if qs.exists():
        return qs
    return []

@register.simple_tag
def get_popular_posts():
    qs = (Post.objects
        .annotate(likes=(Count('votes', filter=Q(votes__like=True)) - Count('votes', filter=Q(votes__like=False))))
        .order_by('-likes', '-created_at'))[:3]
    if qs.exists():
        return qs
    return []

@register.simple_tag
def get_categories_total():
    qs = Category.objects.all().annotate(posts_count=Count('post')).order_by('name')
    if qs.exists():
        return qs
    return []

@register.simple_tag
def get_popular_tags():
    qs = Tag.objects.all()[:6]
    if qs.exists():
        return qs
    return []

@register.simple_tag
def get_archives():
    qs = (Post.objects.annotate(month=ExtractMonth('created_at'), year=ExtractYear('created_at'),)
            .order_by('-year', '-month')
            .values('month', 'year')
            .annotate(total=Count('*'))
            .values('month', 'year', 'total'))[:6]
    if qs.exists():
        return qs
    return []