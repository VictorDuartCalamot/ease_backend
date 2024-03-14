from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to delete it.
    
    """

    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, and OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if the user is the owner of the expense.
        if obj.user == request.user.id:
            return True
        else:
            return False