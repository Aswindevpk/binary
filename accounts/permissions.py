from rest_framework.permissions import BasePermission

class IsUnauthenticated(BasePermission):
    """
    Permission class to restrict access to authenticated user
    """

    def has_permission(self, request, view):
        return not request.user.is_authenticated