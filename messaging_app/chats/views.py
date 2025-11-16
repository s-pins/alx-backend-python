from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User, Conversation, Message
from .serializers import UserSerializer, ConversationSerializer, MessageSerializer

# ---------------- Conversation ViewSet ----------------
class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation with participants.
        Expected request data: {"participants": [user_id1, user_id2, ...]}
        """
        participant_ids = request.data.get('participants', [])
        if not participant_ids:
            return Response({"error": "participants field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        participants = User.objects.filter(user_id__in=participant_ids)
        conversation = Conversation.objects.create()
        conversation.participants.set(participants)
        conversation.save()

        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# ---------------- Message ViewSet ----------------
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def create(self, request, *args, **kwargs):
        """
        Send a new message in an existing conversation.
        Expected request data: {"conversation_id": "...", "sender_id": "...", "message_body": "..."}
        """
        conversation_id = request.data.get('conversation_id')
        sender_id = request.data.get('sender_id')
        message_body = request.data.get('message_body')

        if not all([conversation_id, sender_id, message_body]):
            return Response({"error": "conversation_id, sender_id, and message_body are required"}, status=400)

