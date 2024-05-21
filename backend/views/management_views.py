# backend/views.py
from datetime import datetime
from rest_framework.response import Response
from rest_framework import status,viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError,AuthenticationFailed,PermissionDenied,NotFound
from django.utils import timezone
from django.db.models import Q
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.db import transaction
from guardian.shortcuts import assign_perm
from guardian.models import UserObjectPermission
from backend.utils import filter_by_date_time
from backend.permissions import IsOwnerOrReadOnly,HasMorePermsThanUser
from backend.serializers import ExpenseSerializer, IncomeSerializer, CategorySerializer,SubCategorySerializer,IncomeUpdateSerializer,ExpenseUpdateSerializer,SubCategoryUpdateSerializer,CategoryUpdateSerializer
from backend.models import Expense, Income, Category, SubCategory
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
'''
Este archivo es para las vistas de gastos e ingresos.
'''
#Expenses
@receiver(post_save, sender=Expense)
@receiver(post_delete, sender=Expense)
def clear_expense_cache(sender, instance, **kwargs):
    cache.delete_pattern(f"expense_{instance.user.id}_list_*") 
class ExpenseListView(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated] 
    
    def filter_expense(self, request):
        """Filter expenses based on request parameters."""
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        start_time_str = request.query_params.get('start_time')
        end_time_str = request.query_params.get('end_time')        
        # Convert date strings to datetime objects, handling potential errors
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else timezone.now().date()
            start_time = datetime.strptime(start_time_str, '%H:%M:%S').time() if start_time_str else None
            end_time = datetime.strptime(end_time_str, '%H:%M:%S').time() if end_time_str else None
        except ValueError:
            raise ValidationError({'detail': 'Invalid date format'})
        
        expense_queryset = filter_by_date_time(Expense.objects.filter(user=request.user.id), start_date, end_date, start_time, end_time)        
        return expense_queryset
        
    def get_expense_cache_key(self, request):
        """Generate a cache key based on query parameters."""
        params = request.query_params.dict()
        return f"expense_{request.user.id}_list_{'_'.join(f'{k}_{v}' for k, v in sorted(params.items()))}"
    
    def get(self, request, *args, **kwargs):
        """Override the list method to include caching logic."""
        try:
            cache_key = self.get_expense_cache_key(request)
            cache_expense = cache.get(cache_key)
            
            if cache_expense:
                return Response(cache_expense, status=status.HTTP_200_OK)
            
            expense_queryset = self.filter_expense(request)
            serialized_data = IncomeSerializer(expense_queryset, many=True).data
            
            cache.set(cache_key, serialized_data, timeout=60*15)  # Cache for 15 minutes

            return Response(serialized_data, status=status.HTTP_200_OK)
        except Exception as e:
            raise ValidationError({'detail': 'An error occurred while retrieving the data.'})
            
    def create(self, request, *args, **kwargs):  
        '''
            Post request to create new expense object
        '''              
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            raise AuthenticationFailed({"detail": "User is not authenticated"})  
        if (request.data['amount'] <= 0):
            raise ValidationError({"detail": "Amount is equal or lower than 0"})                      
        #Insert userID into the request.data array
        request.data['user'] = request.user.id                        
        # Create a serializer instance with the data in the array
        serializer = ExpenseSerializer(data=request.data) 
        #Check if the serializer is valid
        if serializer.is_valid():            
            with transaction.atomic():
                # Save the expense object to the database
                instance = serializer.save()
                # Ensure the transaction is committed
                transaction.on_commit(lambda: self.after_create(instance))
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            # Print out the errors for debugging
            raise ValidationError(serializer.errors)  

    def after_create(self, instance):
        '''
        Perform actions after the expense object is created
        '''
        if instance is None:
            print("Error: Expense instance is None in after_create")
            return
        # Assign permissions to the user who created the expense
        assign_perm('change_expense', instance.user, instance)        
        assign_perm('delete_expense', instance.user, instance)
class ExpenseDetailView(viewsets.ModelViewSet):
    '''
        View for requests with specific PK
    '''
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated,IsOwnerOrReadOnly] 

    def get(self,request,pk):
        '''
           Get single expense object with specified PK
        '''      
        try:
            # Retrieve the expense object based on the primary key (pk) and user
            expense = Expense.objects.get(id=pk, user=request.user.id)
        except Expense.DoesNotExist:
            # If the expense object does not exist for the specified user, return a 404 Not Found response
            raise NotFound({'detail': 'Expense not found.'})                
        serializer = ExpenseSerializer(expense)         
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @staticmethod
    @receiver(pre_delete, sender=Expense)
    def delete_object_permissions(sender, instance, **kwargs):
        '''Once the object has been deleted, deletes the permissions associated with it'''
        # Delete associated object permissions
        UserObjectPermission.objects.filter(object_pk=str(instance.pk)).delete()   

    def delete(self, request, pk):
        '''
        Delete expense object with specified PK 
        '''        
        try:
            expense = Expense.objects.get(pk=pk)             
            expense.delete()           
            return Response({'message': 'Expense deleted successfully!'},status=status.HTTP_204_NO_CONTENT)
        except Expense.DoesNotExist:            
            raise NotFound({'detail':f'Expense {pk} not found.'})

    
    def update(self, request, *args,**kwargs):
        '''
            Update expense object with specified PK
        '''
        # Retrieve the expense object
        expense = self.get_object() #The get_object() method retrieves the PK from the URL and looks for the object using that                
        if (request.data['amount'] <= 0):
            raise ValidationError({'detail': 'Amount is equal or lower than 0'})                            
        # Serialize the expense data with the updated data from request
        serializer = ExpenseUpdateSerializer(expense, data=request.data)        
        # Validate the serializer data
        if serializer.is_valid():
            # Save the updated expense object
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            # Return error response if serializer data is invalid
            raise ValidationError(serializer.errors)
#Income
@receiver(post_save, sender=Income)
@receiver(post_delete, sender=Income)
def clear_income_cache(sender, instance, **kwargs):
    cache.delete_pattern(f"income_{instance.user.id}_list_*") 
class IncomeListView(viewsets.ModelViewSet):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer
    permission_classes = [IsAuthenticated] 
    
    def filter_income(self, request):
        """Filter income based on request parameters."""
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        start_time_str = request.query_params.get('start_time')
        end_time_str = request.query_params.get('end_time')        
        # Convert date strings to datetime objects, handling potential errors
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else timezone.now().date()
            start_time = datetime.strptime(start_time_str, '%H:%M:%S').time() if start_time_str else None
            end_time = datetime.strptime(end_time_str, '%H:%M:%S').time() if end_time_str else None
        except ValueError:
            raise ValidationError({'detail': 'Invalid date format'})
        
        income_queryset = filter_by_date_time(Income.objects.filter(user=request.user.id), start_date, end_date, start_time, end_time)        
        return income_queryset
        
    def get_income_cache_key(self, request):
        """Generate a cache key based on query parameters."""
        params = request.query_params.dict()
        return f"income_{request.user.id}_list_{'_'.join(f'{k}_{v}' for k, v in sorted(params.items()))}"
    
    def get(self, request, *args, **kwargs):
        """Override the list method to include caching logic."""
        try:
            cache_key = self.get_income_cache_key(request)
            cache_income = cache.get(cache_key)
            
            if cache_income:
                return Response(cache_income, status=status.HTTP_200_OK)
            
            income_queryset = self.filter_income(request)
            serialized_data = IncomeSerializer(income_queryset, many=True).data
            
            cache.set(cache_key, serialized_data, timeout=60*15)  # Cache for 15 minutes

            return Response(serialized_data, status=status.HTTP_200_OK)
        except Exception as e:
            raise ValidationError({'detail': 'An error occurred while retrieving the data.'})

    def create(self, request, *args, **kwargs):  
        '''
            Post request to create new income object
        '''              
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            raise AuthenticationFailed({'detail': "User is not authenticated"})
        if (request.data['amount'] <= 0):
                raise ValidationError({'detail': 'Amount is equal or lower than 0'})

        #Insert userID into the request.data array
        request.data['user'] = request.user.id
        
        # Create a serializer instance with the data in the array
        serializer = IncomeSerializer(data=request.data) 
        #Check if the serializer is valid
        if serializer.is_valid():            
            with transaction.atomic():
                # Save the expense object to the database
                instance = serializer.save()
                # Ensure the transaction is committed
                transaction.on_commit(lambda: self.after_create(instance))                
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            # Print out the errors for debugging
            raise ValidationError(serializer.errors)

    def after_create(self, instance):
        '''
        Perform actions after the expense object is created
        '''        
        if instance is None:
            return
        # Assign permissions to the user who created the expense
        assign_perm('change_income', instance.user, instance)        
        assign_perm('delete_income', instance.user, instance)     
class IncomeDetailView(viewsets.ModelViewSet):
    '''
        View for requests with specific PK
    '''
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer
    permission_classes = [IsAuthenticated,IsOwnerOrReadOnly] 
     
    def get(self,request,pk):
        '''
           Get single income object with specified PK
        '''      
        try:
        # Retrieve the income object based on the primary key (pk) and user
            income = Income.objects.get(id=pk, user=request.user.id)
        except Income.DoesNotExist:
        # If the income object does not exist for the specified user, return a 404 Not Found response
            raise NotFound({'detail': 'Income not found.'})
                
        serializer = IncomeSerializer(income)         
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @staticmethod
    @receiver(pre_delete, sender=Income)
    def delete_object_permissions(sender, instance, **kwargs):
        # Delete associated object permissions
        UserObjectPermission.objects.filter(object_pk=str(instance.pk)).delete() 

    def delete(self, request, pk):
        '''
            Delete income object with specified PK 
        '''        
        try:
            income = Income.objects.get(pk=pk)            
            income.delete()
            return Response({'message':'Income deleted successfully!'},status=status.HTTP_204_NO_CONTENT)
        except Income.DoesNotExist:
            raise NotFound({'detail':'Income not found.'})
    
    def update(self, request, *args,**kwargs):

        '''
            Update income object with specified PK
        '''
        # Retrieve the income object
        income = self.get_object() #The get_object() method retrieves the PK from the URL and looks for the object using that                
        if not (request.data['amount']):
            raise ValidationError({'detail': 'Couldn`t get amount'})                                    
        else: 
            if (request.data['amount'] <= 0):
                raise ValidationError({'detail': 'Amount is equal or lower than 0'})
        # Serialize the income data with the updated data from request
        serializer = IncomeUpdateSerializer(income, data=request.data)                
        # Validate the serializer data
        if serializer.is_valid():
            # Save the updated income object
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            # Return error response if serializer data is invalid
            raise ValidationError(serializer.errors)
        
@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def clear_category_cache(sender, instance, **kwargs):
    cache.delete_pattern("category_list_*") 
class CategoryListView(viewsets.ModelViewSet):    
    ''''''
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]  

    def filter_categories(self, request):
        """Filter categories based on request parameters."""
        type = request.query_params.get('type', None)
        category_queryset = Category.objects.all()
        
        if type is not None:
            category_queryset = category_queryset.filter(type=type)        
        return category_queryset
        
    def get_category_cache_key(self, request):
        """Generate a cache key based on query parameters."""
        params = request.query_params.dict()
        return f"category_list_{'_'.join(f'{k}_{v}' for k, v in sorted(params.items()))}"
    
    def get(self, request, *args, **kwargs):
        """Override the list method to include caching logic."""
        try:
            cache_key = self.get_category_cache_key(request)
            cache_category = cache.get(cache_key)
            
            if cache_category:
                return Response(cache_category, status=status.HTTP_200_OK)
            
            category_queryset = self.filter_categories(request)
            serialized_data = CategorySerializer(category_queryset, many=True).data
            
            cache.set(cache_key, serialized_data, timeout=60*15)  # Cache for 15 minutes

            return Response(serialized_data, status=status.HTTP_200_OK)
        except Exception as e:
            raise ValidationError({'detail': 'An error occurred while retrieving the data.'})
    
    def create(self,request):   
        '''
        Create new category
        '''       
        if request.user.is_staff == False and request.user.is_superuser == False:
            raise AuthenticationFailed({'detail': 'User has not enough permission'})
        serializer = CategorySerializer(data=request.data) 
        #Check if the serializer is valid
        if serializer.is_valid():            
            serializer.save()  # Save the income object to the database 
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            raise ValidationError(serializer.errors)
      
class CategoryDetailView(viewsets.ModelViewSet):
    ''''''
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated] 
    '''Get,delete,update'''
    def get(self,request,pk):
        '''
           Get single income object with specified PK
        '''      
        try:
        # Retrieve the income object based on the primary key (pk) and user
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
        # If the income object does not exist for the specified user, return a 404 Not Found response
            raise NotFound({'detail': 'Income not found.'})
        serializer = CategorySerializer(category)         
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    def delete(self, request, pk):
        '''
            Delete income object with specified PK 
        '''
        if request.user.is_staff == False and request.user.is_superuser == False:
            raise AuthenticationFailed({'detail': 'User has not enough permission to perform this action'})
        try:
        
            if SubCategory.objects.filter(category=pk).exists() or Expense.objects.filter(category=pk).exists() or Income.objects.filter(category=pk).exists():
                raise ValidationError({'detail': 'Cannot delete subcategory because there are related objects with the specified category'})
            
            category = Category.objects.get(pk=pk)            
            category.delete() 
            return Response({'message':'Category deleted successfully'},status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            raise NotFound({'detail':'Category not found'})
        
    def update(self, request, *args,**kwargs):
        '''
            Update income object with specified PK
        '''
        if request.user.is_staff == False and request.user.is_superuser == False:
            raise AuthenticationFailed({'detail': 'User has not enough permission to perform this action'})
        # Retrieve the income object
        category = self.get_object() #The get_object() method retrieves the PK from the URL and looks for the object using that        
        
        # Serialize the income data with the updated data from request
        serializer = CategoryUpdateSerializer(category, data=request.data)
        
        # Validate the serializer data
        if serializer.is_valid():
            # Save the updated income object
            serializer.save()
            cache_key = f"category_list"
            cache.delete(cache_key) 
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            # Return error response if serializer data is invalid
            raise ValidationError({'detail': f'Error occurred trying to update the category: {serializer.errors}'})
        
@receiver(post_save, sender=SubCategory)
@receiver(post_delete, sender=SubCategory)
def clear_subcategory_cache(sender, instance, **kwargs):
    cache.delete_pattern("subcategory_list_*")     
class SubCategoryListView(viewsets.ModelViewSet):    
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsAuthenticated] 

    def filter_subcategories(self, request):
        """Filter subcategories based on request parameters."""
        category_id = request.query_params.get('category_id', None)
        type = request.query_params.get('type', None)
        subcategory_queryset = SubCategory.objects.all()
        
        if category_id is not None:
            subcategory_queryset = subcategory_queryset.filter(category=category_id) 
        if type is not None:
            subcategory_queryset = subcategory_queryset.filter(type=type)       
        return subcategory_queryset
        
    def get_subcategory_cache_key(self, request):
        """Generate a cache key based on query parameters."""
        params = request.query_params.dict()
        return f"subcategory_list_{'_'.join(f'{k}_{v}' for k, v in sorted(params.items()))}"
    
    def get(self, request, *args, **kwargs):
        """Override the list method to include caching logic."""
        try:
            cache_key = self.get_subcategory_cache_key(request)
            cache_subcategory = cache.get(cache_key)
            
            if cache_subcategory:
                return Response(cache_subcategory, status=status.HTTP_200_OK)
            
            subcategory_queryset = self.filter_subcategories(request)
            serialized_data = SubCategorySerializer(subcategory_queryset, many=True).data
            
            cache.set(cache_key, serialized_data, timeout=60*15)  # Cache for 15 minutes

            return Response(serialized_data, status=status.HTTP_200_OK)
        except Exception as e:
            raise ValidationError({'detail': 'An error occurred while retrieving the data.'})

    def create(self,request):   
        '''
        Create new subcategory
        '''       
        if request.user.is_staff == False and request.user.is_superuser == False:
            raise ValidationError({'detail': 'User has not enough permission'})
        serializer = SubCategorySerializer(data=request.data)         
        #Check if the serializer is valid        
        if serializer.is_valid():                     
            serializer.save()  # Save the income object to the database            
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            raise ValidationError(serializer.errors)

class SubCategoryDetailView(viewsets.ModelViewSet):
    ''''''
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsAuthenticated] 
    '''Get,delete,update'''
    def get(self,request,pk):
        '''
           Get single income object with specified PK
        '''      
        try:
        # Retrieve the income object based on the primary key (pk) and user
            subCategory = SubCategory.objects.get(id=pk)
        except SubCategory.DoesNotExist:
        # If the income object does not exist for the specified user, return a 404 Not Found response
            raise NotFound({'detail': 'Income not found.'})
        serializer = SubCategorySerializer(subCategory)              
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        '''
            Delete income object with specified PK 
        '''
        if request.user.is_staff == False and request.user.is_superuser == False:
            raise AuthenticationFailed({'detail': 'User has not enough permission'})
        try:

            if Expense.objects.filter(subcategory=pk).exists() or Income.objects.filter(subcategory=pk).exists():
                raise ValidationError({'detail': 'Cannot delete subcategory because there are related objects with the specified subcategory'})

            subCategory = SubCategory.objects.get(pk=pk)
            subCategory.delete()                                
            return Response(status=status.HTTP_204_NO_CONTENT)
        except SubCategory.DoesNotExist:
            raise NotFound({'detail': 'Subcategory not found'})
        
    def update(self, request, *args,**kwargs):
        '''
            Update income object with specified PK
        '''
        if request.user.is_staff == False and request.user.is_superuser == False:
            raise AuthenticationFailed({'detail': 'User doesn`t have enough permission'})
        # Retrieve the income object
        subCategory = self.get_object() #The get_object() method retrieves the PK from the URL and looks for the object using that        
        
        # Serialize the income data with the updated data from request
        serializer = SubCategoryUpdateSerializer(subCategory, data=request.data)
        
        # Validate the serializer data
        if serializer.is_valid():
            # Save the updated income object
            serializer.save()            
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            # Return error response if serializer data is invalid
            raise ValidationError(serializer.errors)
