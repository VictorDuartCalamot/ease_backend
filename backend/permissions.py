from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from backend.utils import getUserObjectByEmail
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to delete it.
    
    """
    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, and OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        print('Obj.user: ',obj.user.id)
        print('request.user', request.user.id)
        # Check if the user is the owner of the expense.
        if obj.user == request.user:
            return True
        else:
            raise PermissionDenied("You do not have permission to delete this expense.")
        
class PermissionLevel(permissions.BasePermission):
    '''Check permissions for user'''
    def isSuperUser(self,request):
        '''Check if user is super user'''
        print(self.user)
        userObj = getUserObjectByEmail(self.user)
        if (userObj.get('is_superuser') == True):
            return True
        else:
            raise PermissionDenied("You do not have enough permission.")