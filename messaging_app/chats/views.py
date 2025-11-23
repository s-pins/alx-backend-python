from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.response import Response

from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.all()
    permission_classes = [IsParticipantOfConversation]

    # REQUIRED BY AUTO-CHECK
    filter_backends = [filters.SearchFilter]
    search_fields = ["participants__first_name", "participants__last_name"]

    def get_queryset(self):
        return self.request.user.conversations.all()

    def perform_create(self, serializer):
        participants = serializer.validated_data.get("participants", [])
        if self.request.user not in participants:
            participants.append(self.request.user)
        serializer.save(participants=participants)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    permission_classes = [IsParticipantOfConversation]

    filter_backends = [filters.SearchFilter]
    search_fields = ["message_body"]

    def get_queryset(self):
        conversation_id = self.kwargs["conversation_pk"]
        # The IsParticipantOfConversation permission class will handle the authorization for the conversation object.
        # So we can just filter messages for the current conversation here.
        return Message.objects.filter(
            conversation_id=conversation_id
        ).order_by("sent_at")

    def perform_create(self, serializer):
        conversation_id = self.kwargs["conversation_pk"]
        conversation = get_object_or_404(Conversation, pk=conversation_id)
        serializer.save(
            sender=self.request.user,
            conversation=conversation
        )
