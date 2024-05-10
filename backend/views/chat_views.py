from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from backend.models import ChatSession
from backend.serializers import ChatSessionSerializer
from backend.permissions import HasMorePermsThanUser
from django.db.models import Q
import random

User = get_user_model()

class ChatSessionViewSet(viewsets.ModelViewSet):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='get-or-create-chat')
    def get_or_create_chat(self, request):
        # Filtrar los usuarios que son admins (is_staff) o superadmins (is_superuser)
        admins = User.objects.filter((Q(is_staff=True) | Q(is_superuser=True)) & Q(is_active=True)).order_by('?').first()
        if not admins:
            return Response({'error': 'No admins available'}, status=status.HTTP_404_NOT_FOUND)
        
        # Intentar encontrar un chat activo existente con cualquier admin
        chat = ChatSession.objects.filter(customer=request.user, is_active=True).first()
        if not chat:
            # Si no hay chat activo, crea uno nuevo con un admin aleatorio
            chat = ChatSession.objects.create(customer=request.user, admin=admins, is_active=True)
        
        return Response({'chat_id': chat.id, 'admin_id': admins.id}, status=status.HTTP_200_OK)
    
class ChatSessionDetailViewSet(viewsets.ModelViewSet):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    # Establece las clases de permisos por defecto para todas las acciones en el ViewSet
    permission_classes = [IsAuthenticated, HasMorePermsThanUser]

    @action(detail=True, methods=['post'], url_path='close-chat')
    def close_chat(self, request, pk=None):
        # La variable 'pk' representa la ID del chat específico
        chat = self.get_object()
        if chat:
            chat.is_active = False
            chat.save()
            return Response({'status': 'chat closed', 'chat_id': pk})
        else:
            return Response({'status': 'chat not found'}, status=status.HTTP_404_NOT_FOUND)