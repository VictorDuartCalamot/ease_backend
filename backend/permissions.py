from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
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
            raise PermissionDenied("You do not have enough permissions.")
        

class IsSuperUser(permissions.BasePermission):
    '''Check permissions for user'''
    
    def isSuperUser(self, user):
        '''Check if user is super user'''      
        return user.is_superuser

    def has_permission(self, request, view):
        '''Check if user has permission for the request'''
        print(request)
        user = request.user
        print(f'Checking permissions for user: {user}')
        if self.isSuperUser(user):
            print('User is a superuser.')
            return True
        else:
            print('User is not a superuser.')
            return False
    
class HasEnoughPerms(permissions.BasePermission):
    print('Entra siquiera? ? ? ? ?')
    '''Rule to check if user has enough permissions'''
    def has_object_permission(self, request, view, obj):
        print('Pero entra dentro??')
        
        # Allow GET, HEAD, and OPTIONS requests.                
        # Check if the user is the owner of the expense.
        
        if request.user.is_superuser:
            return True
        elif request.user.is_staff and (obj.user.is_superuser or obj.user.is_staff) == False:
            return True
        else:
            return False
        