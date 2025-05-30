from rest_framework import permissions

class IsTaskManagerOrAssignee(permissions.BasePermission):
    """
    Custom permission to only allow project managers or task assignees to edit tasks.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to project members
        if request.method in permissions.SAFE_METHODS:
            return obj.project.is_member(request.user)

        # Write permissions are only allowed to the project manager or task assignee
        return (obj.project.manager == request.user or 
                obj.assigned_to == request.user)

class IsProjectMemberForTask(permissions.BasePermission):
    """
    Custom permission to only allow project members to view tasks.
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            project_id = request.data.get('project')
            if not project_id:
                return False
            from projects.models import Project
            try:
                project = Project.objects.get(id=project_id)
                return project.is_member(request.user)
            except Project.DoesNotExist:
                return False
        return True

    def has_object_permission(self, request, view, obj):
        return obj.project.is_member(request.user)

class CanCommentOnTask(permissions.BasePermission):
    """
    Custom permission to only allow project members to comment on tasks.
    """
    def has_permission(self, request, view):
        task_id = view.kwargs.get('task_id')
        if task_id:
            from .models import Task
            try:
                task = Task.objects.get(id=task_id)
                return task.project.is_member(request.user)
            except Task.DoesNotExist:
                return False
        return True 