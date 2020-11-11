from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from taggit.managers import TaggableManager

from mptt.models import MPTTModel, TreeForeignKey

class Category(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ('name', )

class Post(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='blog/', default='default_post.jpg')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    tags = TaggableManager(blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.pk})

    def get_comments(self):
        return self.comments.count()

    def get_votes(self):
        return self.votes.count()

    def get_likes(self):
        return self.votes.filter(like=True).count()

    def get_dislikes(self):
        return self.votes.filter(like=False).count()

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(default=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return 'Comment by {}'.format(self.author.username)

    def get_votes(self):
        return self.votes.count()

    def get_likes(self):
        return self.votes.filter(like=True).count()

    def get_dislikes(self):
        return self.votes.filter(like=False).count()

class Vote(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    like = models.BooleanField(default=True)
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE, related_name='votes')
    comment = models.ForeignKey(Comment, null=True, blank=True, on_delete=models.CASCADE, related_name='votes')

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return 'Vote by {}'.format(self.author.username)