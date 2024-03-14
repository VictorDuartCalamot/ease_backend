# backend/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status,viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.http import Http404
from rest_framework import generics
from backend.permissions import IsOwner
from backend.serializers import ExpenseSerializer
from backend.models import Expense
from django.contrib.auth.models import User
from backend.serializers import UserSerializerWithToken
'''
class ExpenseView(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        print("Entramos en el post")  
        #print(request.user.pk)                              
        #userdata = UserSerializerWithToken(request.user).data
        request.data['user'] = request.user.pk
        #serializer = ExpenseSerializer(data=request.data, context={'user': request.user.pk}) 
        serializer = ExpenseSerializer(data=request.data) 
        #print(serializer)           
        #print(userdata)
        if serializer.is_valid():
            print('Valida el serializer?')
            serializer.save()  # Save the expense object to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # Print out the errors for debugging
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     '''   
class ExpenseView(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        print("Entered the post method")
        
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            return Response({"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Assign the user to the expense
        request.data['user'] = request.user.id
        
        # Print request data for debugging
        print("Request data:", request.data)
        
        # Create a serializer instance with the request data
        serializer = ExpenseSerializer(data=request.data) 
        
        if serializer.is_valid():
            print('Serializer is valid')
            serializer.save()  # Save the expense object to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # Print out the errors for debugging
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)