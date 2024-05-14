import logging
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from backend.models import Income,Expense
from backend.serializers import IncomeSerializer,ExpenseSerializer
from backend.serializers import UserSerializer

logger = logging.getLogger(__name__)
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to delete it.    
    """
    def has_permission(self, request, view):
        # Determine the type of object (income or expense) based on the view name
        model = view.get_view_name().lower().split()
        if 'income' in model[0]:
            obj_model = Income
            obj_serializer = IncomeSerializer
        elif 'expense' in model[0]:
            obj_model = Expense
            obj_serializer = ExpenseSerializer
        else:
            # If the object type cannot be determined, deny permission
            return False
        
        # Retrieve the object based on the primary key (pk) from the request URL        
        obj_pk = view.kwargs.get('pk')       
        try:
            obj = obj_model.objects.get(pk=obj_pk)
            serializer = obj_serializer(obj)            
            #logging.debug(serializer.data,request.user.id)
            if serializer.data['user'] == request.user.id:
                #logging.debug('Owner')
                return True
            else:                
                return False        
        except obj_model.DoesNotExist:            
            return False                
        
        

class IsSuperUser(permissions.BasePermission):
    '''Check permissions for user'''
    
    def isSuperUser(self, user):
        '''Check if user is super user'''      
        return user.is_superuser

    def has_permission(self, request, view):
        '''Check if user has permission for the request'''        
        user = request.user
        #logging.debug(f'Checking permissions for user: {user}')
        if self.isSuperUser(user):
            #logging.debug('User is a superuser.')
            return True
        else:
            #logging.debug('User is not a superuser.')
            return False

class HasMorePermsThanUser(permissions.BasePermission):
    '''Checks if the user has more permissions than a normal user'''    
    def isSuperUser(self, user):
        '''Check if user is super user'''      
        return user.is_superuser
    def isStaff(self,user):
        return user.is_staff
    def has_permission(self, request, view):
        '''Check if user has permission for the request'''        
        user = request.user
        #logger.debug(f'Checking permissions for user: {user}')
        if self.isSuperUser(user) or self.isStaff(user):
            #logger.debug(f'{user} is superuser or staff')
            return True
        else:
            #logging.debug('User is not a superuser or staff.')
            return False  


class HasEnoughPerms(permissions.BasePermission):    
    '''
        Checks user permission and object(User) permission
        (If the user has more or less permission than the object(user) that is being modified)
    '''            
    def has_permission(self, request, view):
        user_pk = view.kwargs.get('pk')
        try:
            user = User.objects.get(pk=user_pk)
            serializer = UserSerializer(user)
            #logger.debug(f'Serializer Data: {serializer.data}')
        except User.DoesNotExist:
            return False
        
        # Check if the user is a superuser or staff member
        if request.user.is_superuser:
            return True
        elif request.user.is_staff:
            if serializer.data.get('is_superuser') == True or serializer.data.get('is_staff') == True:
                #logger.debug(f'{request.user} tried to modify a staff or superuser')                
                return False
            else:
                #logger.debug(f'Staff user: {request.user} modified a user')                                
                return True                        
        else:
            #logger.debug(f'{request.user} is neither a superuser nor a staff member.')
            return False