from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import Follow
from apps.posts.models import Like, Mention

from .models import Notification


@receiver(post_save, sender=Like)
def handle_like_notification(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.post.author == instance.user:
        return
    Notification.objects.create(
        recipient=instance.post.author,
        actor=instance.user,
        verb=Notification.Verb.LIKE,
        target_post=instance.post,
    )


@receiver(post_save, sender=Follow)
def handle_follow_notification(sender, instance, created, **kwargs):
    if not created:
        return
    Notification.objects.create(
        recipient=instance.following,
        actor=instance.follower,
        verb=Notification.Verb.FOLLOW,
    )


@receiver(post_save, sender=Mention)
def handle_mention_notification(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.user == instance.post.author:
        return
    Notification.objects.create(
        recipient=instance.user,
        actor=instance.post.author,
        verb=Notification.Verb.MENTION,
        target_post=instance.post,
    )
