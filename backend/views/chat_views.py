from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from backend.models import ChatSession
from backend.serializers import ChatSessionSerializer
from backend.permissions import HasMorePermsThanUser
from django.db.models import Q
from rest_framework.exceptions import ValidationError,AuthenticationFailed,PermissionDenied,NotFound
import random

User = get_user_model()
class ChatSessionViewSet(viewsets.ModelViewSet):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='get-or-create-chat')
    def get_or_create_chat(self, request):
        '''
            Fetch existing chat session with the current user, if there is none create one
        '''                       
        # Firstly tries to find a existing chat session with the user
        chat = ChatSession.objects.filter(customer=request.user, is_active=True).first()
        if not chat:
            # If there is no existing chat session create a new one with a random admin
            admins = User.objects.filter((Q(is_staff=True) | Q(is_superuser=True)) & Q(is_active=True)).order_by('?').first()
            if not admins:
                #logger.error(f'No admins available to create a new chat session')
                raise NotFound({'detail': 'No admins available'})
            chat = ChatSession.objects.create(customer=request.user, admin=admins, is_active=True)
        
        return Response({'chat_id': chat.id}, status=status.HTTP_200_OK)
    
class ChatSessionDetailViewSet(viewsets.ModelViewSet):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    # Establece las clases de permisos por defecto para todas las acciones en el ViewSet
    permission_classes = [IsAuthenticated, HasMorePermsThanUser]

    @action(detail=True, methods=['post'], url_path='close-chat')
    def close_chat(self, request, pk=None):
        '''
            As a admin or superuser delete the specified chat session
        '''
        # La variable 'pk' representa la ID del chat específico
        chat = self.get_object()
        if chat:
            chat.delete()
            return Response({'message': f'chat {pk} closed'},status=status.HTTP_202_ACCEPTED)
        else:
            raise NotFound({'detail': 'chat not found'})