from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('adminsite/', admin.site.urls),
    path('api/superadmin/', include('backend.urls.admin_urls')),
    path('api/users/', include('backend.urls.user_urls')),
    path('api/management/', include('backend.urls.management_urls')),   
    path('api/', include('backend.urls.openAI_chat_urls')),   
]
