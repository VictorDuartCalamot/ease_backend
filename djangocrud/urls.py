from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('backend.urls.user_urls')),
    path('api/management/', include('backend.urls.management_urls')),   
]
