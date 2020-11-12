from django.dispatch import receiver
from django.db.models.signals import post_save
from blog.models import Comment, Vote
from .models import Notification

@receiver(post_save, sender=Comment)
@receiver(post_save, sender=Vote)
def notificate(sender, instance, created, **kwargs):
    print(created, instance.author, sender.__name__)
    if created:
        if instance.author:
            if sender.__name__=="Comment":
                Notification.commentNotification.createNotification(instance)
            elif sender.__name__=="Vote":
                Notification.voteNotification.createNotification(instance)