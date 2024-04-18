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
    '''Rule to check if user has enough permissions'''
    def has_object_permission(self, request, view, obj):
        
        # Allow GET, HEAD, and OPTIONS requests.        
        print('Obj.user: ',obj.user.is_superuser,obj.user.is_staff,obj.user.is_active)
        print('request.user', request.user.is_superuser,request.user.is_staff,request.user.is_active)
        # Check if the user is the owner of the expense.
        if obj.user == request.user:
            return True
        else:
            raise PermissionDenied("You do not have permission to delete this expense.")

                
            
