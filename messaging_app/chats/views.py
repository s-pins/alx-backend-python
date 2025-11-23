from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.all()

    def perform_create(self, serializer):
        participants = serializer.validated_data.get("participants", [])

        # ensure creating user is in the participants list
        if self.request.user not in participants:
            participants.append(self.request.user)

        serializer.save(participants=participants)

    def get_queryset(self):
        # only show conversations the user participates in
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related("participants", "messages")
        

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer

    def get_queryset(self):
        conversation_id = self.kwargs["conversation_pk"]

        return Message.objects.filter(
            conversation_id=conversation_id,
            conversation__participants=self.request.user
        ).select_related("sender").order_by("sent_at")

    def perform_create(self, serializer):
        conversation_id = self.kwargs["conversation_pk"]
        conversation = get_object_or_404(Conversation, pk=conversation_id)

        # Only participants can send messages
        if self.request.user not in conversation.participants.all():
            raise PermissionDenied("You are not part of this conversation.")

        serializer.save(sender=self.request.user, conversation=conversation)
