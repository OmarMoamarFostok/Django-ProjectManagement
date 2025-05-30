from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date
from projects.models import Project
from tasks.models import Task
from .models import Notification

class NotificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.manager = User.objects.create_user(username='manager', password='manager123')
        self.member = User.objects.create_user(username='member', password='member123')
        
        # Create project
        self.project = Project.objects.create(
            title='Test Project',
            description='Test Description',
            manager=self.manager,
            start_date=date.today(),
            end_date=date(2024, 12, 31)
        )
        self.project.members.add(self.member)
        
        # Create task
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            project=self.project,
            assigned_to=self.member,
            status='todo',
            due_date=date(2024, 12, 31)
        )

    def test_notification_creation(self):
        """Test notification creation on task assignment"""
        notification = Notification.objects.filter(
            recipient=self.member,
            notification_type='task_assigned'
        ).first()
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.content_type, ContentType.objects.get_for_model(self.task))
        self.assertEqual(notification.object_id, self.task.id)

    def test_notification_listing(self):
        """Test notification listing endpoint"""
        self.client.force_authenticate(user=self.member)
        url = reverse('notification-list')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) > 0)

    def test_mark_notification_read(self):
        """Test marking notification as read"""
        self.client.force_authenticate(user=self.member)
        notification = Notification.objects.filter(recipient=self.member).first()
        url = reverse('notification-update', args=[notification.id])
        
        response = self.client.patch(url, {'is_read': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_mark_all_notifications_read(self):
        """Test marking all notifications as read"""
        # Create multiple notifications
        Notification.objects.create(
            recipient=self.member,
            notification_type='project_updated',
            title='Project Updated',
            message='Project details were updated',
            content_type=ContentType.objects.get_for_model(self.project),
            object_id=self.project.id
        )
        
        self.client.force_authenticate(user=self.member)
        url = reverse('mark-all-notifications-read')
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        unread_count = Notification.objects.filter(
            recipient=self.member,
            is_read=False
        ).count()
        self.assertEqual(unread_count, 0)

    def test_notification_permissions(self):
        """Test notification access permissions"""
        notification = Notification.objects.filter(recipient=self.member).first()
        url = reverse('notification-update', args=[notification.id])
        
        # Test access by wrong user
        self.client.force_authenticate(user=self.manager)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Test access by correct user
        self.client.force_authenticate(user=self.member)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK) 