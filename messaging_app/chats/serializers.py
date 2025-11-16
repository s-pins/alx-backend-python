from rest_framework import serializers
from .models import User, Conversation, Message

# ---------- User Serializer ----------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'created_at']


# ---------- Message Serializer ----------
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)  # Include sender info in the message

    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'message_body', 'sent_at']


# ---------- Conversation Serializer ----------
class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)  # Include participants
    messages = MessageSerializer(many=True, read_only=True)   # Include nested messages

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'created_at']
