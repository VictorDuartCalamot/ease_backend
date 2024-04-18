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
    


'''
def isSuperUser(self, user):
    
    return user.is_superuser
def isStaff(self, user): 
    return user.is_staff
        '''
class HasEnoughPerms(permissions.BasePermission):    
    '''Rule to check if user has enough permissions'''
    
        
    def has_permission(self, request, view):
        user_pk = view.kwargs.get('pk')
        try:
            user = User.objects.get(pk=user_pk)
            serializer = UserSerializer(user)
            print(serializer.data)
        except User.DoesNotExist:
            return False
        
        # Check if the user is a superuser or staff member
        if request.user.is_superuser:
            print('User is a superuser.')
            return True
        elif request.user.is_staff:
            print('User is a staff member.')
            return True
        else:
            print('User is neither a superuser nor a staff member.')
            return False