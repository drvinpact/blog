from django.contrib import admin
from .models import Post, Comment, Vote

class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at']
    list_display_links = ['title', 'author']
    list_filter = ['author']
    readonly_fields = ['created_at']

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

