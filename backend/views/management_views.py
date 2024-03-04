# backend/views.py

from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from backend.models import Income, Expense
from backend.serializers import IncomeSerializer, ExpenseSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.http import Http404
from rest_framework import generics
from backend.permissions import IsOwner

"""
class IncomeView(APIView):
    #permission_classes = [IsAuthenticated]   
    #authentication_classes = [TokenAuthentication] 
    def post(self, request):
        print('Postin!')
        print(request.data)
        # Deserialize request data
        serializer = IncomeSerializer(data=request.data)
        if serializer.is_valid():
            # Assign the authenticated user to the expense
            serializer.save()
            #serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""

class ExpenseView(APIView):
    #permission_classes = [IsAuthenticated]    
    #authentication_classes = [TokenAuthentication]
    @api_view(['POST'])
    def post(self, request):
        print('Postin!')
        print(request.data)
        # Deserialize request data
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid():
            # Assign the authenticated user to the expense
            serializer.save()
            #serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
