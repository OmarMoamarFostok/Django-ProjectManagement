from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date
from projects.models import Project
from .models import Task, Comment

class TaskTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.manager = User.objects.create_user(username='manager', password='manager123')
        self.member = User.objects.create_user(username='member', password='member123')
        self.other_user = User.objects.create_user(username='other', password='other123')
        
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

    def test_create_task(self):
        """Test task creation"""
        self.client.force_authenticate(user=self.manager)
        url = reverse('task-list')
        data = {
            'title': 'New Task',
            'description': 'New Description',
            'project': self.project.id,
            'assigned_to_id': self.member.id,
            'status': 'todo',
            'due_date': '2024-12-31'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)

    def test_task_permissions(self):
        """Test task permissions"""
        url = reverse('task-detail', args=[self.task.id])
        
        # Test non-project member access
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Test assignee access
        self.client.force_authenticate(user=self.member)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test assignee update
        response = self.client.patch(url, {'status': 'in_progress'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test manager update
        self.client.force_authenticate(user=self.manager)
        response = self.client.put(url, {
            'title': 'Updated Task',
            'description': self.task.description,
            'project': self.project.id,
            'assigned_to_id': self.member.id,
            'status': 'done',
            'due_date': '2024-12-31'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_task_filtering(self):
        """Test task filtering and search"""
        self.client.force_authenticate(user=self.manager)
        
        # Create additional task for testing
        Task.objects.create(
            title='Another Task',
            description='Another Description',
            project=self.project,
            assigned_to=self.member,
            status='in_progress',
            due_date=date(2024, 6, 30)
        )
        
        url = reverse('task-list')
        
        # Test status filter
        response = self.client.get(f'{url}?status=in_progress')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test search
        response = self.client.get(f'{url}?search=Another')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_comments(self):
        """Test task comments"""
        self.client.force_authenticate(user=self.member)
        url = reverse('task-comments', args=[self.task.id])
        
        # Test creating comment
        data = {'content': 'Test comment'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        
        # Test listing comments
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test comment permissions
        comment = Comment.objects.first()
        url = reverse('comment-detail', args=[self.task.id, comment.id])
        
        # Other user shouldn't be able to delete the comment
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Comment creator should be able to delete it
        self.client.force_authenticate(user=self.member)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0) 