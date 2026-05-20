from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source='actor.username', read_only=True)
    actor_avatar = serializers.URLField(source='actor.avatar_url', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'actor', 'actor_username', 'actor_avatar',
            'verb', 'target_post', 'is_read', 'created_at',
        ]
        read_only_fields = ['id', 'recipient', 'actor', 'verb', 'target_post', 'created_at']
