from django.urls import path
from backend.views import user_views as user_views


urlpatterns = [
    path('management/user/', user_views.SuperAdminManagementDetailView.as_view({'post':'createUserWithRoles','delete':'','put':''}), name='admin-register'),
    
]
