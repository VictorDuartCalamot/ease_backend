from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from backend.serializers import UserSerializer
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to delete it.
    
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, and OPTIONS requests.        
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
    def isSuperUser(self, user):
        '''Check if user is super user'''      
        return user.is_superuser
    def isStaff(self, user):
        '''Check if user is super user'''      
        return user.is_staff
        
    def has_permission(self, request, view,pk):
        user = request.user
        userObj = User.objects.get(id=pk)
        serializer = UserSerializer(userObj)  
        print(serializer.data)
        if self.isSuperUser(user):            
            print('User is a super user')
            return True
        elif self.isStaff(user):
            print('User is a staff user')
            return True
        else:
            print('User is not a super user or staff user')
            return False