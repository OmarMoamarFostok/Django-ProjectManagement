from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from projects.models import Project
from tasks.models import Task, Comment
from .models import Notification

@receiver(post_save, sender=Task)
def task_notification(sender, instance, created, **kwargs):
    if created:
        # Notify project manager about new task
        if instance.project.manager != instance.assigned_to:
            Notification.objects.create(
                recipient=instance.project.manager,
                notification_type='task_created',
                title='New Task Created',
                message=f'A new task "{instance.title}" has been created in project "{instance.project.title}"',
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id
            )
        
        # Notify assigned user
        if instance.assigned_to != instance.project.manager:
            Notification.objects.create(
                recipient=instance.assigned_to,
                notification_type='task_assigned',
                title='Task Assigned',
                message=f'You have been assigned to task "{instance.title}" in project "{instance.project.title}"',
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id
            )
    else:
        # Notify relevant users about task updates
        if instance.assigned_to != instance.project.manager:
            Notification.objects.create(
                recipient=instance.assigned_to,
                notification_type='task_updated',
                title='Task Updated',
                message=f'Task "{instance.title}" has been updated',
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id
            )

@receiver(post_save, sender=Comment)
def comment_notification(sender, instance, created, **kwargs):
    if created:
        # Notify task assignee about new comment
        if instance.user != instance.task.assigned_to:
            Notification.objects.create(
                recipient=instance.task.assigned_to,
                notification_type='task_commented',
                title='New Comment',
                message=f'New comment on task "{instance.task.title}"',
                content_type=ContentType.objects.get_for_model(instance.task),
                object_id=instance.task.id
            )
        
        # Notify project manager about new comment
        if instance.user != instance.task.project.manager:
            Notification.objects.create(
                recipient=instance.task.project.manager,
                notification_type='task_commented',
                title='New Comment',
                message=f'New comment on task "{instance.task.title}"',
                content_type=ContentType.objects.get_for_model(instance.task),
                object_id=instance.task.id
            )

@receiver(post_save, sender=Project)
def project_notification(sender, instance, created, **kwargs):
    if created:
        # Notify members about being added to the project
        for member in instance.members.all():
            if member != instance.manager:
                Notification.objects.create(
                    recipient=member,
                    notification_type='project_added',
                    title='Added to Project',
                    message=f'You have been added to project "{instance.title}"',
                    content_type=ContentType.objects.get_for_model(instance),
                    object_id=instance.id
                )
    else:
        # Notify members about project updates
        for member in instance.members.all():
            if member != instance.manager:
                Notification.objects.create(
                    recipient=member,
                    notification_type='project_updated',
                    title='Project Updated',
                    message=f'Project "{instance.title}" has been updated',
                    content_type=ContentType.objects.get_for_model(instance),
                    object_id=instance.id
                ) 