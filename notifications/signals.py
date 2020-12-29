from django.dispatch import receiver
from django.db.models.signals import post_save
from blog.models import Comment, Vote
from messenger.models import Message
from .models import Notification

@receiver(post_save, sender=Comment)
@receiver(post_save, sender=Vote)
@receiver(post_save, sender=Message)
def notificate(sender, instance, created, **kwargs):
    if sender.__name__=="Comment":
        if created:
            Notification.commentNotification.createNotification(instance)
    elif sender.__name__=="Message":
        if created:
            Notification.messageNotification.createNotification(instance)
    elif sender.__name__=="Vote":
        Notification.voteNotification.createNotification(instance)