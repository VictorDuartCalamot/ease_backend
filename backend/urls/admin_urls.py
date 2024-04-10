from django.urls import path
from backend.views import user_views as user_views


urlpatterns = [
    path('superadmin/user/', user_views.SuperAdminManagementListView.as_view({'get':'getAllUsers','post':'createUserWithRoles'}), name='superuser-tools'),
    path('superadmin/user/<uuid:pk>/', user_views.SuperAdminManagementDetailView.as_view({'delete':'createUserWithRoles','update':'updateUser'}), name='superuser-tools2'),
    
]
