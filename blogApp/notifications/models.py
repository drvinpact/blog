from django.db import models
from django.contrib.auth.models import User
from blog.models import Post, Comment, Vote
from django.urls import reverse

class CommentNotification(models.Manager):
    def createNotification(self, obj):
        category = 'comment'        
        author = obj.author
        post = obj.post
        parent = obj.parent

        if parent:
            user = parent.author
            action = 'replied'
            html_message = "{} {} to your comment on {}"
            message = html_message.format(author, action, post)
        else:
            user = post.author
            action = 'commented'
            html_message = "{} {} on your post {}"
            message = html_message.format(author, action, post)

        Notification.objects.create(
            user=user,
            author=author,
            post=post,
            comment=parent,
            category=category,
            action=action,
            message=message,
            html_message=html_message
        )

class VoteNotification(models.Manager):
    def createNotification(self, obj):
        category = 'vote'
        author = obj.author        
        comment = obj.comment
        action = 'likes' if obj.like else 'dislikes'

        if comment:              
            post = comment.post  
            user = comment.author
            html_message = "{} {} your comment on {}"
            message = html_message.format(author, action, post)
        else:
            post = obj.post
            user = post.author
            html_message = "{} {} your post {}"
            message = html_message.format(author, action, post)

        Notification.objects.create(
            user=user,
            author=author,
            post=post,
            comment=comment,
            category=category,
            action=action,
            message=message,
            html_message=html_message
        )
        
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author', null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    message = models.TextField()
    html_message = models.TextField()
    read = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    category = models.CharField(max_length=255)
    action = models.CharField(max_length=255, null=True)

    objects = models.Manager()
    commentNotification = CommentNotification()
    voteNotification = VoteNotification()

    class Meta:
        ordering = ['-created_at']

    def get_html_message(self):
        author_url = reverse('blog:user_profile', kwargs={'slug': self.author})
        author = "<a href='{}'>{}</a>".format(author_url, self.author)
        post_url = reverse('blog:post_detail', kwargs={'pk': self.post.id})
        post = "<a href='{}'><i>{}</i></a>".format(post_url, self.post)

        return self.html_message.format(author, self.action, post)