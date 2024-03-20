from django.urls import path
from backend.views import management_views as management_views

urlpatterns = [    
    #Expense
    path('expense/', management_views.ExpenseListView.as_view({'get':'get','post':'create'}), name='expense-list'),
    path('expense/<uuid:pk>/', management_views.ExpenseDetailView.as_view({'get':'get','delete':'delete','put':'update'}), name='expense-detail'),
    #Income
    path('income/', management_views.IncomeListView.as_view({'get':'get','post':'create'}), name='income-list'),
    path('income/<uuid:pk>/', management_views.IncomeDetailView.as_view({'get':'get','delete':'delete','put':'update'}), name='income-detail'),
    
]


    
