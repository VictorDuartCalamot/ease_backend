# backend/views.py

from datetime import datetime
from rest_framework.response import Response
from rest_framework import status,viewsets
from rest_framework.permissions import IsAuthenticated
from backend.permissions import IsOwnerOrReadOnly,HasMorePermsThanUser
from backend.serializers import ExpenseSerializer, IncomeSerializer, CategorySerializer,SubCategorySerializer
from backend.models import Expense, Income, Category, SubCategory
from django.utils import timezone
from django.db.models import Q
from backend.utils import filter_by_date_time


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
        #print(start_date_str,'-',end_date_str)        
        # Convert date strings to datetime objects, handling potential errors
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else timezone.now().date()
            start_time = datetime.strptime(start_time_str, '%H:%M:%S').time() if start_time_str else None
            end_time = datetime.strptime(end_time_str, '%H:%M:%S').time() if end_time_str else None
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
        
        #print(f'Start date {start_date}, end date: {end_date}, start time: {start_time}, end time: {end_time}')
        expenses_queryset = filter_by_date_time(Expense.objects.filter(user=request.user.id), start_date, end_date, start_time, end_time)
        
        print(expenses_queryset)        
        # Serialize the expenses
        serializer = ExpenseSerializer(expenses_queryset, many=True)
        #print('Serializer ok?', serializer.data)        
        # Return a JSON response containing the serialized expenses
        return Response(serializer.data, status=status.HTTP_200_OK)
            
    def create(self, request, *args, **kwargs):  
        '''
            Post request to create new expense object
        '''              
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            return Response({"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)  
        if (request.data['amount'] <= 0):
            return Response({"error": "Amount is equal or lower than 0"}, status=status.HTTP_400_BAD_REQUEST)                      
        #Insert userID into the request.data array
        request.data['user'] = request.user.id                        
        # Create a serializer instance with the data in the array
        serializer = ExpenseSerializer(data=request.data) 
        #Check if the serializer is valid
        if serializer.is_valid():            
            serializer.save()  # Save the expense object to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            #print(serializer.errors)  # Print out the errors for debugging
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
        
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
            return Response({'error': 'Expense not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        #print(expense)
        serializer = ExpenseSerializer(expense) 
        #print(serializer.data)        
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def delete(self, request, pk):
        '''
            Delete expense object with specified PK 
        '''
        #print('Inside delete request')
        try:
            expense = Expense.objects.get(pk=pk)
            #print(expense)
            expense.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Expense.DoesNotExist:
            return Response("Expense not found.", status=status.HTTP_404_NOT_FOUND)

    
    def update(self, request, *args,**kwargs):
        '''
            Update expense object with specified PK
        '''
        # Retrieve the expense object
        expense = self.get_object() #The get_object() method retrieves the PK from the URL and looks for the object using that        
        if (request.data['amount'] <= 0):
            return Response({"error": "Amount is equal or lower than 0"}, status=status.HTTP_400_BAD_REQUEST)            
        request.data['user'] = request.user.id        
        request.data['creation_date'] = expense.creation_date
        request.data['creation_time'] = expense.creation_time
        # Serialize the expense data with the updated data from request
        serializer = ExpenseSerializer(expense, data=request.data)
        
        # Validate the serializer data
        if serializer.is_valid():
            # Save the updated expense object
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Return error response if serializer data is invalid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#Income
class IncomeListView(viewsets.ModelViewSet):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer
    permission_classes = [IsAuthenticated] 
    
    def get(self, request):     
        '''
            Get to retrieve data filtered by dates 
        '''   
        #print('Inside get request')
        # Get query parameters for date range
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        start_time_str = request.query_params.get('start_time')
        end_time_str = request.query_params.get('end_time')
        #print(start_date_str,'-',end_date_str)
        print(end_date_str,start_date_str,start_time_str,end_time_str)
        # Convert date strings to datetime objects, handling potential errors
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else timezone.now().date()
            start_time = datetime.strptime(start_time_str, '%H:%M:%S').time() if start_time_str else None
            end_time = datetime.strptime(end_time_str, '%H:%M:%S').time() if end_time_str else None
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
        
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
            return Response({"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)            
        if (request.data['amount'] <= 0):
            return Response({"error": "Amount is equal or lower than 0"}, status=status.HTTP_400_BAD_REQUEST)            

        #Insert userID into the request.data array
        request.data['user'] = request.user.id
        
        # Create a serializer instance with the data in the array
        serializer = IncomeSerializer(data=request.data) 
        #Check if the serializer is valid
        if serializer.is_valid():            
            serializer.save()  # Save the income object to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            #print(serializer.errors)  # Print out the errors for debugging
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
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
            return Response({'error': 'Income not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        #print(income)
        serializer = IncomeSerializer(income) 
        #print(serializer.data)        
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def delete(self, request, pk):
        '''
            Delete income object with specified PK 
        '''
        #print('Inside delete request')
        try:
            income = Income.objects.get(pk=pk)
            #print(income)
            income.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Income.DoesNotExist:
            return Response("Income not found.", status=status.HTTP_404_NOT_FOUND)

    #TODO: Fixear fecha hora para que no se sobreescriba
    def update(self, request, *args,**kwargs):

        '''
            Update income object with specified PK
        '''
        # Retrieve the income object
        income = self.get_object() #The get_object() method retrieves the PK from the URL and looks for the object using that        
        request.data['user'] = request.user.id
        request.data['creation_date'] = income.creation_date
        request.data['creation_time'] = income.creation_time
        # Serialize the income data with the updated data from request
        serializer = IncomeSerializer(income, data=request.data)
        
        # Validate the serializer data
        if serializer.is_valid():
            # Save the updated income object
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Return error response if serializer data is invalid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            return Response({'error': 'Category objects not found.'}, status=status.HTTP_404_NOT_FOUND)               

    def create(self,request):   
        '''
        Create new category
        '''       
        if request.user.is_staff == False and request.user.is_superuser == False:
            return Response({"error": "User has not enough permission"}, status=status.HTTP_403_FORBIDDEN)    
        serializer = CategorySerializer(data=request.data) 
        #Check if the serializer is valid
        if serializer.is_valid():            
            serializer.save()  # Save the income object to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            #print(serializer.errors)  # Print out the errors for debugging
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

        
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
            category = Category.objects.get(id=pk)
        except Category.DoesNotExist:
        # If the income object does not exist for the specified user, return a 404 Not Found response
            return Response({'error': 'Income not found.'}, status=status.HTTP_404_NOT_FOUND)        
        #print(income)
        serializer = CategorySerializer(category) 
        #print(serializer.data)        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        '''
            Delete income object with specified PK 
        '''
        if request.user.is_staff == False and request.user.is_superuser == False:
            return Response({"error": "User has not enough permission"}, status=status.HTTP_403_FORBIDDEN)           
        try:
            category = Category.objects.get(pk=pk)            
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return Response("Income not found.", status=status.HTTP_404_NOT_FOUND)
        
    def update(self, request, *args,**kwargs):
        '''
            Update income object with specified PK
        '''
        if request.user.is_staff == False and request.user.is_superuser == False:
            return Response({"error": "User has not enough permission"}, status=status.HTTP_403_FORBIDDEN)
        # Retrieve the income object
        category = self.get_object() #The get_object() method retrieves the PK from the URL and looks for the object using that        
        
        # Serialize the income data with the updated data from request
        serializer = CategorySerializer(category, data=request.data)
        
        # Validate the serializer data
        if serializer.is_valid():
            # Save the updated income object
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Return error response if serializer data is invalid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class SubCategoryListView(viewsets.ModelViewSet):
    ''''''
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsAuthenticated] 
    '''Get,Create'''

class SubCategoryDetailView(viewsets.ModelViewSet):
    ''''''
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsAuthenticated] 
    '''Get,delete,update'''
