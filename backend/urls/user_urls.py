from django.urls import path
from backend.views import user_views as user_views

'''
Este archivo es para tener los endpoints delos usuarios
'''

urlpatterns = [
    path('login/', user_views.MyTokenObtainPairView.as_view(),
        name='token_obtain_pair'),
    path('register/', user_views.registerUser, name='register'),
    path('logout/', user_views.LogoutView.as_view({'get':'get'}), name='logout'),
    path('loginLog/', user_views.AuthUserLogsListView.as_view({'get':'get','post':'create'}), name='log-list'),
    path('loginLog/<uuid:pk>/', user_views.AuthUserLogsDetailView.as_view({'get':'get','delete':'delete','put':'update'}), name='log-detail'),
    path('changepwd/',user_views.change_password, name='change_password'),
]
