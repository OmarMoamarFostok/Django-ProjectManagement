from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date
from .models import Project

class ProjectTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.manager = User.objects.create_user(
            username='manager',
            password='manager123'
        )
        self.member = User.objects.create_user(
            username='member',
            password='member123'
        )
        self.non_member = User.objects.create_user(
            username='nonmember',
            password='nonmember123'
        )
        
        # Create a project
        self.project = Project.objects.create(
            title='Test Project',
            description='Test Description',
            manager=self.manager,
            start_date=date.today(),
            end_date=date(2024, 12, 31)
        )
        self.project.members.add(self.member)

    def test_create_project(self):
        """Test project creation"""
        self.client.force_authenticate(user=self.manager)
        url = reverse('project-list')
        data = {
            'title': 'New Project',
            'description': 'New Description',
            'start_date': '2023-01-01',
            'end_date': '2023-12-31',
            'member_ids': [self.member.id]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)

    def test_project_permissions(self):
        """Test project permissions"""
        url = reverse('project-detail', args=[self.project.id])
        
        # Test non-member access
        self.client.force_authenticate(user=self.non_member)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Test member access
        self.client.force_authenticate(user=self.member)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test member update (should fail)
        response = self.client.put(url, {'title': 'Updated Title'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test manager update (should succeed)
        self.client.force_authenticate(user=self.manager)
        response = self.client.put(url, {
            'title': 'Updated Title',
            'description': self.project.description,
            'start_date': self.project.start_date,
            'end_date': self.project.end_date
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_project_filtering(self):
        """Test project filtering and search"""
        self.client.force_authenticate(user=self.manager)
        
        # Create additional project for testing
        Project.objects.create(
            title='Another Project',
            description='Another Description',
            manager=self.manager,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )
        
        url = reverse('project-list')
        
        # Test search by title
        response = self.client.get(f'{url}?search=Another')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test ordering
        response = self.client.get(f'{url}?ordering=-created_at')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2) 