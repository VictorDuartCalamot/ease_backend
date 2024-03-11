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


class ExpenseView(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        print("Entramos en el post")        
        user_pk = request.user.pk 
        
        user_instance = User.objects.get(id=user_pk) 
       
        print(user_pk)
        print(user_instance)
        serializer = ExpenseSerializer(data=request.data, context={'user': user_instance}) 
        print(serializer)    
        
        if serializer.is_valid():
            print('Valida el serializer?')
            serializer.save()  # Save the expense object to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # Print out the errors for debugging
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)