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

class IncomeView(APIView):
    permission_classes = [IsAuthenticated]   
    authentication_classes = [TokenAuthentication] 

    def get_object(self, pk):
        try:
            return Income.objects.get(pk=pk, user=self.request.user)
        except Income.DoesNotExist:
            raise Http404
        
    def post(self, request):
            serializer = IncomeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)  # Assign the authenticated user to the expense
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request, pk):
        income = self.get_object(pk)
        serializer = IncomeSerializer(income)
        return Response(serializer.data)
        
    def put(self, request, pk):
        income = self.get_object(pk)
        serializer = IncomeSerializer(income, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        income = self.get_object(pk)
        income.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExpenseView(APIView):
    #permission_classes = [IsAuthenticated]    
    #authentication_classes = [TokenAuthentication]
    
    def get_object(self, pk):
        try:
            return Expense.objects.get(pk=pk, user=self.request.user)
        except Expense.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        expense = self.get_object(pk)
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data)
    
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
    
    def put(self, request, pk):
        expense = self.get_object(pk)
        serializer = ExpenseSerializer(expense, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        expense = self.get_object(pk)
        expense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


