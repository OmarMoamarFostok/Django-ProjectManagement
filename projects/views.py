from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project
from .serializers import ProjectSerializer
from .permissions import IsProjectManagerOrReadOnly, IsProjectMember
from django.db import models

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsProjectManagerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'start_date', 'end_date']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        This view should return a list of all projects
        for the currently authenticated user.
        """
        user = self.request.user
        return Project.objects.filter(
            models.Q(manager=user) | models.Q(members=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user) 