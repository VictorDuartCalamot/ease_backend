from django.urls import path
from backend.views.chat_views import ChatSessionViewSet, ChatSessionDetailViewSet

'''
    Endpoints for chat sessions
'''
urlpatterns = [
    path('chat', ChatSessionDetailViewSet.as_view({'get': 'getChats'}), name='getChats'),
    path('get-or-create/', ChatSessionViewSet.as_view({'post': 'get_or_create_chat'}), name='get-or-create-chat'),
    path('<int:pk>/close/', ChatSessionDetailViewSet.as_view({'post': 'close_chat'}), name='close-chat'),    
     
]