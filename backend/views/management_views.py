# backend/views.py

from datetime import datetime
from rest_framework.response import Response
from rest_framework import status,viewsets
from rest_framework.permissions import IsAuthenticated , DjangoObjectPermissions
from backend.serializers import ExpenseSerializer
from backend.models import Expense
from django.shortcuts import get_object_or_404
from django.utils import timezone
from guardian.shortcuts import get_objects_for_user
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.http import Http404
from rest_framework import generics
from django.contrib.auth.models import User
from backend.serializers import UserSerializerWithToken


class ExpenseListView(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated] 
    
    def get(self, request):     
        '''
            Get to retrieve data filtered by dates 
        '''   
        print('Inside get request')
        # Get query parameters for date range
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        print(start_date_str,'-',end_date_str)

        # Convert date strings to datetime objects, handling potential errors
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else timezone.now().date()
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
        
        print('Usuario',request.user.id)
        print('Start date',start_date)
        print('End Date',end_date)

        # Filter expenses based on date range
        expenses = Expense.objects.filter(user=request.user.id)
        
        if start_date is not None and end_date is not None:
            print('Inside both fullfilled values')
            if start_date == end_date:
                print('Both are the same dates')
                expenses = expenses.filter(creation_date=start_date)
            else:
                print('Different dates, range')
                expenses = expenses.filter(creation_date__range=[start_date, end_date])
        elif start_date is not None:
            print('Start date is fullfilled')
            expenses = expenses.filter(creation_date__gte=start_date)
        elif end_date is not None:   
            print('End date is fullfilled')         
            expenses = expenses.filter(creation_date__lte=end_date)

        print('Filtered expenses:', expenses)
        
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
            print(serializer.errors)  # Print out the errors for debugging
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ExpenseDetailView(viewsets.ModelViewSet):
    '''
        View for requests with specific PK
    '''
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]  

    def get(self,request,pk):
        '''
           Get single expense object with specified PK
        '''      
        print(self)  
        print(request)
        print(object)
        expense = Expense.objects.filter(user=request.user.id,id=pk)
        print(expense)
        serializer = ExpenseSerializer(expense) 
        print(serializer.data)
        # Retrieve the expense object based on the primary key (pk)
        if serializer.data:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    
    def delete(self, request, pk):
        '''
            Delete expense object with specified PK 
        '''
        print('Inside delete request')
        try:
            expense = Expense.objects.get(pk=pk)
            print(expense)
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
        