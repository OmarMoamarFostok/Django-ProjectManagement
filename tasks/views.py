from rest_framework import viewsets, generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task, Comment
from .serializers import TaskSerializer, CommentSerializer
from .permissions import IsTaskManagerOrAssignee, IsProjectMemberForTask, CanCommentOnTask
from django_filters import rest_framework as django_filters

class TaskFilter(django_filters.FilterSet):
    due_date_before = django_filters.DateFilter(field_name='due_date', lookup_expr='lte')
    due_date_after = django_filters.DateFilter(field_name='due_date', lookup_expr='gte')

    class Meta:
        model = Task
        fields = {
            'status': ['exact'],
            'project': ['exact'],
            'assigned_to': ['exact'],
            'is_pinned': ['exact'],
        }

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsTaskManagerOrAssignee]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'is_pinned']
    ordering = ['-is_pinned', '-created_at']

    def get_queryset(self):
        """
        This view should return a list of all tasks
        for projects the user is a member of.
        """
        user = self.request.user
        return Task.objects.filter(
            project__in=user.managed_projects.all() |
            user.member_projects.all()
        ).distinct()

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [CanCommentOnTask]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']

    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs['task_id'])

    def perform_create(self, serializer):
        serializer.save(
            task_id=self.kwargs['task_id'],
            user=self.request.user
        )

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [CanCommentOnTask]

    def get_queryset(self):
        return Comment.objects.filter(
            task_id=self.kwargs['task_id'],
            user=self.request.user
        ) 