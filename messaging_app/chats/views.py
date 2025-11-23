from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import User, Conversation, Message
from .serializers import (
    UserSerializer,
    ConversationSerializer,
    MessageSerializer,
)


# -------------------- Conversation ViewSet --------------------
class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation.
        Expected JSON:
        {
            "participants": ["uuid1", "uuid2", ...]
        }
        """
        participant_ids = request.data.get("participants")

        if not participant_ids:
            return Response(
                {"error": "participants field is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        participants = User.objects.filter(user_id__in=participant_ids)

        if not participants.exists():
            return Response(
                {"error": "No valid participants found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        conversation = Conversation.objects.create()
        conversation.participants.set(participants)

        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        """
        Custom endpoint:
        GET /conversations/<id>/messages/
        """
        conversation = get_object_or_404(Conversation, conversation_id=pk)
        messages = Message.objects.filter(conversation=conversation)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=200)


# -------------------- Message ViewSet --------------------
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def create(self, request, *args, **kwargs):
        """
        Send a message to a conversation.
        Expected JSON:
        {
            "conversation_id": "...",
            "sender_id": "...",
            "recipient_id": "...",   # optional depending on your model
            "message_body": "Hello!"
        }
        """
        conversation_id = request.data.get("conversation_id")
        sender_id = request.data.get("sender_id")
        recipient_id = request.data.get("recipient_id")  # optional
        message_body = request.data.get("message_body")

        if not conversation_id or not sender_id or not message_body:
            return Response(
                {
                    "error": "conversation_id, sender_id, and message_body are required"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        conversation = get_object_or_404(Conversation, conversation_id=conversation_id)
        sender = get_object_or_404(User, user_id=sender_id)

        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            recipient_id=recipient_id,
            message_body=message_body,
        )

        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
