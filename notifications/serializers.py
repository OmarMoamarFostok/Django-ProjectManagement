from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'notification_type', 'title',
            'message', 'is_read', 'content_type', 'object_id',
            'created_at'
        ]
        read_only_fields = [
            'recipient', 'notification_type', 'title',
            'message', 'content_type', 'object_id', 'created_at'
        ]

    def update(self, instance, validated_data):
        instance.is_read = validated_data.get('is_read', instance.is_read)
        instance.save()
        return instance 