from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, ProjectLog

class ProjectMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class ProjectLogSerializer(serializers.ModelSerializer):
    user = ProjectMemberSerializer(read_only=True)

    class Meta:
        model = ProjectLog
        fields = ['id', 'user', 'action', 'details', 'created_at']
        read_only_fields = ['user']

class ProjectSerializer(serializers.ModelSerializer):
    manager = ProjectMemberSerializer(read_only=True)
    members = ProjectMemberSerializer(many=True, read_only=True)
    logs = ProjectLogSerializer(many=True, read_only=True)
    member_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'manager', 'members',
            'member_ids', 'start_date', 'end_date', 'created_at',
            'updated_at', 'logs'
        ]
        read_only_fields = ['manager', 'created_at', 'updated_at']

    def create(self, validated_data):
        member_ids = validated_data.pop('member_ids', [])
        project = Project.objects.create(
            manager=self.context['request'].user,
            **validated_data
        )
        
        # Add members
        if member_ids:
            members = User.objects.filter(id__in=member_ids)
            project.members.add(*members)
            
        # Create log entry
        ProjectLog.objects.create(
            project=project,
            user=self.context['request'].user,
            action='created',
            details=f'Project "{project.title}" was created'
        )
        
        return project

    def update(self, instance, validated_data):
        member_ids = validated_data.pop('member_ids', None)
        
        # Update project fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update members if provided
        if member_ids is not None:
            instance.members.clear()
            members = User.objects.filter(id__in=member_ids)
            instance.members.add(*members)
            
        # Create log entry
        ProjectLog.objects.create(
            project=instance,
            user=self.context['request'].user,
            action='updated',
            details=f'Project "{instance.title}" was updated'
        )
        
        return instance 