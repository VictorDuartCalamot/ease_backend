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
from django.core.cache import cache
User = get_user_model()
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Signal to invalidate cache when a chat session is saved or deleted
@receiver(post_save, sender=ChatSession)
@receiver(post_delete, sender=ChatSession)
def clear_cache(sender, instance, **kwargs):
    print(instance)
    user_id = instance.admin.id
    cache_key = f"user_{user_id}_chats"
    cache.delete(cache_key)
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
            # Invalidate the cache for the user
            cache_key = f"user_{request.user.id}_chats"
            cache.delete(cache_key)
        
        return Response({'chat_id': chat.id}, status=status.HTTP_200_OK)
    
class ChatSessionDetailViewSet(viewsets.ModelViewSet):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    # Establece las clases de permisos por defecto para todas las acciones en el ViewSet
    permission_classes = [IsAuthenticated, HasMorePermsThanUser]

    @action(detail=False, methods=['get'], url_path='get-chats')
    def getChats(self, request):
        '''
        Retrieve all chat sessions for the authenticated user
        '''
        try:
            user = request.user.id
            cache_key = f"user_{user}_chats"
            chat_sessions = cache.get(cache_key)

            if chat_sessions is None:
                chat_sessions = ChatSession.objects.filter(Q(admin=user))
                if not chat_sessions.exists():
                    raise NotFound({'detail': 'No chat sessions found for the user.'})
                cache.set(cache_key, list(chat_sessions), timeout=60*15)  # Cache for 15 minutes

            serializer = ChatSessionSerializer(chat_sessions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except NotFound as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='close-chat')
    def close_chat(self, request, pk=None):
        '''
            As a admin or superuser delete the specified chat session
        '''
        # La variable 'pk' representa la ID del chat específico
        chat = self.get_object()
        if chat:
            chat.delete()
            cache_key = f"user_{request.user.id}_chats"
            cache.delete(cache_key)
            return Response({'message': f'chat {pk} closed'},status=status.HTTP_202_ACCEPTED)
        else:
            raise NotFound({'detail': 'chat not found'})