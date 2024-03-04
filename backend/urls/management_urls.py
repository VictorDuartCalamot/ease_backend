from django.urls import path
from backend.views import management_views as management_views

urlpatterns = [
    #path('income/', management_views.IncomeView.as_view(), name='income-list'),
    path('expense/', management_views.createExpense.as_view(), name='expense-list'),
    
]


    
