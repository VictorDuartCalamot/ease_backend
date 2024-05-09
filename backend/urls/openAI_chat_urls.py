from django.urls import path
from backend.views import openAI_chat_views as chat_views

'''
Este archivo es para tener los endpoints delos usuarios
'''

urlpatterns = [
    path('chat/',chat_views.ChatAPIView.as_view(), name='chat_api'),
]
