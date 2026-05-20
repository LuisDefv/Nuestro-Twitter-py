import re

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import User

from .models import Hashtag, HashtagPost, Mention, Post


@receiver(post_save, sender=Post)
def parse_hashtags_and_mentions(sender, instance, created, **kwargs):
    HashtagPost.objects.filter(post=instance).delete()
    Mention.objects.filter(post=instance).delete()

    hashtag_names = set(re.findall(r'#(\w+)', instance.content))
    for name in hashtag_names:
        hashtag, _ = Hashtag.objects.get_or_create(name=name.lower())
        HashtagPost.objects.get_or_create(hashtag=hashtag, post=instance)

    usernames = set(re.findall(r'@(\w+)', instance.content))
    for username in usernames:
        try:
            user = User.objects.get(username__iexact=username)
            Mention.objects.get_or_create(post=instance, user=user)
        except User.DoesNotExist:
            pass
