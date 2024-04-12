from django.urls import path
from backend.views import user_views as user_views


urlpatterns = [
    path('user/', user_views.SuperAdminManagementListView.as_view({'get':'getAllUsers','post':'createUserWithRoles'}), name='superuser-tools'),
    path('user/<int:pk>/', user_views.SuperAdminManagementDetailView.as_view({'delete':'deleteUser','put':'updateUser'}), name='superuser-tools2'),
    
]
