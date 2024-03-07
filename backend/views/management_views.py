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
        user = request.user    
        print(user)
        serializer = ExpenseSerializer(data=request.data, context={'user': user})
        print(serializer)        
        if serializer.is_valid():
<<<<<<< HEAD
            serializer.save(user=user.pk)  # Save the expense object to the database
=======
            serializer.save(user=user)  # Save the expense object to the database
>>>>>>> 78111347c5d4676c11efb659c147cd405e5acc2e
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # Print out the errors for debugging
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)