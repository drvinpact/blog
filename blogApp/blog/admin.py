from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Category, Post, Comment, Vote

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    list_display_links = ['name']    
    readonly_fields = ['created_at']

class PostAdmin(SummernoteModelAdmin, admin.ModelAdmin):
    summernote_fields = ['content']
    list_display = ['title', 'author', 'category', 'tag_list', 'created_at']
    list_display_links = ['title', 'author', 'category']
    list_filter = ['author']
    readonly_fields = ['created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')
    
    def tag_list(self, obj):
        return ", ".join(o.name for o in obj.tags.all())

class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at']
    list_display_links = ['author', 'post']
    list_filter = ['author', 'post']
    readonly_fields = ['created_at']

class VoteAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'comment', 'like', 'created_at']
    list_display_links = ['author', 'post', 'comment']
    list_filter = ['author', 'post']
    readonly_fields = ['created_at']

admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(Category, CategoryAdmin)

