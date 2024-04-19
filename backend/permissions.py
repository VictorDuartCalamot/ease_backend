from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from backend.models import Income,Expense
from backend.serializers import IncomeSerializer,ExpenseSerializer

from backend.serializers import UserSerializer
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to delete it.
    
    """
    def has_permission(self, request, view):
        # Determine the type of object (income or expense) based on the view name
        if 'income' in view.get_view_name().lower():
            obj_model = Income
        elif 'expense' in view.get_view_name().lower():
            obj_model = Expense
        else:
            # If the object type cannot be determined, deny permission
            return False
        
        # Retrieve the object based on the primary key (pk) from the request URL
        user_pk = view.kwargs.get('pk')
        try:
            obj = obj_model.objects.get(pk=user_pk)
            serializer = IncomeSerializer(obj) if obj_model == Income else ExpenseSerializer(obj)
            print(serializer.data)
        except obj_model.DoesNotExist:
            return False        
        # Check if the user is authenticated
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, and OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if the user is the owner of the object.
        if obj.user == request.user or obj.user_id == request.user.id:
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
    '''Checks user permission and object permission'''            
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
            if serializer.data.get('is_superuser') == True or serializer.data.get('is_staff') == True:
                print('Staff tried to modify a staff or superuser')
                return False
            else:
                print('User is a staff member. Modifying a user')
                return True                        
        else:
            print('User is neither a superuser nor a staff member.')
            return False