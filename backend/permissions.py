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
            raise PermissionDenied("You do not have permission to delete this expense.")
        

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
    print('hallo()&_&(_*&(_()?)(?)(??))')
    def has_enough_permission(self, request, obj):
        # Get the user model
        User = get_user_model()
        print(request.user)
        print(obj)
        # Check if the request.user is a superuser
        is_superuser = request.user.is_superuser

        # Check if the object being managed is a staff member
        if isinstance(obj, User):
            is_staff = obj.is_staff
            is_superuser = obj.is_superuser
        else:
            is_staff = getattr(obj, 'is_staff', False)

        # Superusers can manage anything
        if is_superuser:
            return True
        # Staff members can manage users (with lower permissions) but not other staff members or superusers
        elif is_staff:
            # Check if the request.user is also a staff member
            return not request.user.is_superuser
        # Regular users (non-staff) cannot manage other staff members or superusers
        else:
            return False

                
            
