from rest_framework import permissions

class IsProjectManagerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow project managers to edit or delete projects.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return obj.is_member(request.user)

        # Write permissions are only allowed to the project manager
        return obj.manager == request.user

class IsProjectMember(permissions.BasePermission):
    """
    Custom permission to only allow project members to access project details.
    """
    def has_object_permission(self, request, view, obj):
        return obj.is_member(request.user) 