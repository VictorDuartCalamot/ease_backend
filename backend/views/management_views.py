# backend/views.py
from datetime import datetime
from rest_framework.response import Response
from rest_framework import status,viewsets
from rest_framework.permissions import IsAuthenticated
from backend.permissions import IsOwnerOrReadOnly,HasMorePermsThanUser
from backend.serializers import ExpenseSerializer, IncomeSerializer, CategorySerializer,SubCategorySerializer,IncomeUpdateSerializer,ExpenseUpdateSerializer
from backend.models import Expense, Income, Category, SubCategory
from django.utils import timezone
from django.db.models import Q
from backend.utils import filter_by_date_time
from django.db import transaction
from guardian.shortcuts import assign_perm
from guardian.models import UserObjectPermission
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError,AuthenticationFailed,PermissionDenied,NotFound
'''
Este archivo es para las vistas de gastos e ingresos.
'''
#Expenses
class ExpenseListView(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated] 
    
    def get(self, request):     
        '''
            Get to retrieve data filtered by dates 
        '''   
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
            raise ValidationError({'detail': 'Invalid date/time format'})
                
        expenses_queryset = filter_by_date_time(Expense.objects.filter(user=request.user.id), start_date, end_date, start_time, end_time)
                     
        # Serialize the expenses
        serializer = ExpenseSerializer(expenses_queryset, many=True)              
        # Return a JSON response containing the serialized expenses
        return Response(serializer.data, status=status.HTTP_200_OK)
            
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
class IncomeListView(viewsets.ModelViewSet):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer
    permission_classes = [IsAuthenticated] 
    
    def get(self, request):     
        '''
            Get to retrieve data filtered by dates 
        '''           
        # Get query parameters for date range
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
        
        income = filter_by_date_time(Income.objects.filter(user=request.user.id), start_date, end_date, start_time, end_time)
        # Apply combined date and time filtering        
        serializer = IncomeSerializer(income, many=True)        
        # Return a JSON response containing the serialized Income
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    
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


class CategoryListView(viewsets.ModelViewSet):    
    ''''''
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]  

    '''Get,Create'''
    def get(self,request):
        '''
           Get all categories
        '''      
        try:
        # Retrieve the income object based on the primary key (pk) and user
            category = Category.objects.all()
            serializer = CategorySerializer(category, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
        # If the income object does not exist for the specified user, return a 404 Not Found response
            raise NotFound({'detail': 'Category objects not found.'})

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
        serializer = CategorySerializer(category, data=request.data)
        
        # Validate the serializer data
        if serializer.is_valid():
            # Save the updated income object
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            # Return error response if serializer data is invalid
            raise ValidationError({'detail': f'Error occurred trying to update the category: {serializer.errors}'})
class SubCategoryListView(viewsets.ModelViewSet):
    ''''''
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsAuthenticated] 
    '''Get,Create'''    
    def get(self,request):
        '''
           Get all categories
        '''      
        try:
            category_id = request.query_params.get('category_id',None)
        # Retrieve the income object based on the primary key (pk) and user
            subCategory_queryset = SubCategory.objects.all()
            if category_id is not None:
                subCategory_queryset = subCategory_queryset.filter(category=category_id)
            serializer = SubCategorySerializer(subCategory_queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
        # If the income object does not exist for the specified user, return a 404 Not Found response
            raise NotFound({'detail': 'Category objects not found.'})

    def create(self,request):   
        '''
        Create new category
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
        serializer = SubCategorySerializer(subCategory, data=request.data)
        
        # Validate the serializer data
        if serializer.is_valid():
            # Save the updated income object
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            # Return error response if serializer data is invalid
            raise ValidationError(serializer.errors)
