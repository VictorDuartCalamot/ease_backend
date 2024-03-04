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

    def create(self,request):
        print("Entramos en el post")        
        user = User.objects.get(email=request.user)     
        print(request.data)  
        print(user.pk)  
        serializer = ExpenseSerializer(data=request.data,context={'user': user.pk})
        print(serializer)        
        if serializer.is_valid():
            serializer.save()  # Save the expense object to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)