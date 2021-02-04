from django.db import models
from django.contrib.auth.models import User
from blog.models import Post, Comment, Vote
from messenger.models import Thread
from django.urls import reverse

class CommentNotification(models.Manager):
    def createNotification(self, obj):
        category = 'comment'        
        author = obj.author
        post = obj.post
        parent = obj.parent

        if parent:
            user = parent.author
            if user.id==author.id:
                return
            action = 'respondido'
            html_message = "{} ha {} tu comentario en el cuento {}"            
        else:
            user = post.author
            if user.id==author.id:
                return
            action = 'comentado'
            html_message = "{} ha {} tu cuento {}"
        
        author_name = author.username if author else obj.name
        message = html_message.format(author_name, action, post)

        Notification.objects.create(
            user=user,
            author=author,
            author_name=obj.name,
            post=post,
            comment=parent,
            category=category,
            action=action,
            message=message,
            html_message=html_message
        )

class VoteNotification(models.Manager):
    def createNotification(self, obj):
        comment = obj.comment
        category = 'vote'
        author = obj.author        
        action = 'le agrada' if obj.like else 'no le agrada'

        if comment:
            user = comment.author
            post = comment.post  
            if not user or user.id==author.id:
                return
            html_message = "A {} {} tu comentario en el cuento {}"            
        else:
            post = obj.post
            user = post.author
            if user.id==author.id:
                return
            html_message = "A {} {} tu cuento {}"
        
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

class MessageNotification(models.Manager):
    def createNotification(self, obj):
        category = 'message'
        action = 'nuevo mensaje'
        thread = obj.thread
        users = thread.users.exclude(pk=obj.user.id)
        html_message = "Tienes un {} de {}"

        for user in users:
            message = html_message.format(action, obj.user)
            Notification.objects.create(
                user=user,
                author=obj.user,
                thread=thread,
                category=category,
                action=action,
                message=message,
                html_message=html_message
            )        
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author', null=True)
    author_name = models.CharField(max_length=255, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, null=True)
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
    messageNotification = MessageNotification()

    class Meta:
        ordering = ['-created_at']

    def get_html_message(self):
        # if self.category=='comment' or self.category=='vote':   
        #     if self.author:
        #         author_url = reverse('blog:user_profile', kwargs={'slug': self.author})
        #         img_url = "<img src='{}' class='avatar-notification'>".format(self.author.profile.image.url)
        #         author = "<a href='{}'>{}{}</a>".format(author_url, img_url, self.author)
        #     else:
        #         author = self.author_name
        #     comment = "?comment_id={}".format(self.comment.id) if self.comment.id else ""
        #     post_url = reverse('blog:post_detail', kwargs={'pk': self.post.id}) + comment
        #     post = "<a href='{}'><i>{}</i></a>".format(post_url, self.post)

        #     return self.html_message.format(author, self.action, post)
            
        # elif self.category=='message':
        #     author_url = reverse('blog:user_profile', kwargs={'slug': self.author})
        #     img_url = "<img src='{}' class='avatar-notification'>".format(self.author.profile.image.url)
        #     author = "<a href='{}'>{}{}</a>".format(author_url, img_url, self.author)
        #     thread_url = reverse('messenger:detail', kwargs={'pk': self.thread.id})
        #     thread = "<a href='{}'>{}</a>".format(thread_url, self.action)

        #     return self.html_message.format(thread, author)
        return ""