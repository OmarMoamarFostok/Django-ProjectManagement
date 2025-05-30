from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task, Comment, TaskLog
from projects.serializers import ProjectMemberSerializer

class CommentSerializer(serializers.ModelSerializer):
    user = ProjectMemberSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at', 'updated_at']
        read_only_fields = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class TaskLogSerializer(serializers.ModelSerializer):
    user = ProjectMemberSerializer(read_only=True)

    class Meta:
        model = TaskLog
        fields = ['id', 'user', 'action', 'details', 'created_at']
        read_only_fields = ['user']

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = ProjectMemberSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    logs = TaskLogSerializer(many=True, read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'assigned_to',
            'assigned_to_id', 'status', 'due_date', 'is_pinned',
            'created_at', 'updated_at', 'comments', 'logs'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        assigned_to_id = validated_data.pop('assigned_to_id')
        assigned_to = User.objects.get(id=assigned_to_id)
        task = Task.objects.create(
            assigned_to=assigned_to,
            **validated_data
        )
        
        # Create log entry
        TaskLog.objects.create(
            task=task,
            user=self.context['request'].user,
            action='created',
            details=f'Task "{task.title}" was created'
        )
        
        return task

    def update(self, instance, validated_data):
        if 'assigned_to_id' in validated_data:
            assigned_to_id = validated_data.pop('assigned_to_id')
            instance.assigned_to = User.objects.get(id=assigned_to_id)
        
        # Update task fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Create log entry
        TaskLog.objects.create(
            task=instance,
            user=self.context['request'].user,
            action='updated',
            details=f'Task "{instance.title}" was updated'
        )
        
        return instance 