from django.urls import path
from backend.views import user_views as user_views
from backend.views import management_views as management_views


urlpatterns = [
    path('login/', user_views.MyTokenObtainPairView.as_view(),
        name='token_obtain_pair'),
    path('register/', user_views.registerUser, name='register'),
]
