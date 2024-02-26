from django.urls import path
from backend.views import management_views as management_views

urlpatterns = [
    path('income/', management_views.IncomeView.as_view(), name='income-list'),
    path('expense/', management_views.ExpenseView.as_view(), name='expense-list'),
    path('expenses2/', management_views.ExpenseListCreateAPIView.as_view(), name='expense-list-create'),
    path('expenses2/<int:pk>/', management_views.ExpenseRetrieveUpdateDestroyAPIView.as_view(), name='expense-detail'),
    
]


    
