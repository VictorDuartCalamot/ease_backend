# backend/views.py

from datetime import datetime
from rest_framework.response import Response
from rest_framework import status,viewsets
from rest_framework.permissions import IsAuthenticated
from backend.permissions import IsOwnerOrReadOnly
from backend.serializers import ExpenseSerializer, IncomeSerializer
from backend.models import Expense, Income
from django.utils import timezone
from django.db.models import Q
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
            end_time = datetime.strptime(end_time_str, '%H:%M:%S').time() if end_time_str else timezone.now().time()
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Ensure start_date is not after end_date
        if (start_date and end_date) and (start_date > end_date):
            return Response({'error': 'Start date cannot be after end date.'}, status=status.HTTP_400_BAD_REQUEST)

        if (start_time and end_time) and (start_time > end_time):
            return Response({'error': 'Start time cannot be after end time.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Filter expenses based on date range
        expenses = Expense.objects.filter(user=request.user.id)
        date_query = Q()
        if start_date is not None and end_date is not None:
            if start_date == end_date:
                date_query &= Q(creation_date__date=start_date)
            else:
                date_query &= Q(creation_date__date__range=[start_date, end_date])
        elif start_date is not None:
            date_query &= Q(creation_date__date__gte=start_date)
        elif end_date is not None:   
            date_query &= Q(creation_date__date__lte=end_date)

        time_query = Q()
        if start_time is not None and end_time is not None:
            if start_time == end_time:
                time_query &= Q(creation_date__time=start_time)
            else:
                time_query &= Q(creation_date__time__range=[start_time, end_time])
        elif start_time is not None:
            time_query &= Q(creation_date__time__gte=start_time)
        elif end_time is not None:   
            time_query &= Q(creation_date__time__lte=end_time)
                                 
        # Apply combined date and time filtering
        authUserLog = authUserLog.filter(date_query & time_query)
        # Serialize the expenses
        serializer = ExpenseSerializer(expenses, many=True)        
        # Return a JSON response containing the serialized expenses
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    
    def create(self, request, *args, **kwargs):  
        '''
            Post request to create new expense object
        '''              
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            return Response({"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)            
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
        request.data['user'] = request.user.id
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

        # Convert date strings to datetime objects, handling potential errors
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else timezone.now().date()
            start_time = datetime.strptime(start_time_str, '%H:%M:%S').time() if start_time_str else None
            end_time = datetime.strptime(end_time_str, '%H:%M:%S').time() if end_time_str else timezone.now().time()
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Ensure start_date is not after end_date
        if (start_date and end_date) and (start_date > end_date):
            return Response({'error': 'Start date cannot be after end date.'}, status=status.HTTP_400_BAD_REQUEST)

        if (start_time and end_time) and (start_time > end_time):
            return Response({'error': 'Start time cannot be after end time.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Filter income based on date range
        income = Income.objects.filter(user=request.user.id)
        
        date_query = Q()
        if start_date is not None and end_date is not None:
            if start_date == end_date:
                date_query &= Q(creation_date__date=start_date)
            else:
                date_query &= Q(creation_date__date__range=[start_date, end_date])
        elif start_date is not None:
            date_query &= Q(creation_date__date__gte=start_date)
        elif end_date is not None:   
            date_query &= Q(creation_date__date__lte=end_date)

        time_query = Q()
        if start_time is not None and end_time is not None:
            if start_time == end_time:
                time_query &= Q(creation_date__time=start_time)
            else:
                time_query &= Q(creation_date__time__range=[start_time, end_time])
        elif start_time is not None:
            time_query &= Q(creation_date__time__gte=start_time)
        elif end_time is not None:   
            time_query &= Q(creation_date__time__lte=end_time)
                                 
        # Apply combined date and time filtering
        authUserLog = authUserLog.filter(date_query & time_query)
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

    
    def update(self, request, *args,**kwargs):

        '''
            Update income object with specified PK
        '''
        # Retrieve the income object
        income = self.get_object() #The get_object() method retrieves the PK from the URL and looks for the object using that        
        request.data['user'] = request.user.id
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
