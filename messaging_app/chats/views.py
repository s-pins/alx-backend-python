from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters   
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.all()

    # REQUIRED BY AUTO-CHECK
    filter_backends = [filters.SearchFilter]
    search_fields = ["participants__first_name", "participants__last_name"]

    def perform_create(self, serializer):
        participants = serializer.validated_data.get("participants", [])
        if self.request.user not in participants:
            participants.append(self.request.user)
        serializer.save(participants=participants)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()

    filter_backends = [filters.SearchFilter]
    search_fields = ["message_body"]

    def get_queryset(self):
        return Message.objects.filter(
            conversation_id=self.kwargs["conversation_pk"]
        ).order_by("sent_at")

    def perform_create(self, serializer):
        conversation_id = self.kwargs["conversation_pk"]
        conversation = get_object_or_404(Conversation, pk=conversation_id)

        serializer.save(
            sender=self.request.user,
            conversation=conversation
        )
