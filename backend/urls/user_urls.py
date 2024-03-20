from django.urls import path
from backend.views import user_views as user_views


urlpatterns = [
    path('login/', user_views.MyTokenObtainPairView.as_view(),
        name='token_obtain_pair'),
    path('register/', user_views.registerUser, name='register'),
    path('loginLog/', user_views.AuthUserLogsListView.as_view({'get':'get','post':'create'}), name='income-list'),
    path('loginLog/<uuid:pk>/', user_views.AuthUserLogsDetailView.as_view({'get':'get','delete':'delete','put':'update'}), name='income-detail'),
]
