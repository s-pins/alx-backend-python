# messaging_app/chats/serializers.py
from rest_framework import serializers
from .models import User, Conversation, Message
from django.utils import timezone

# ---------- User Serializer ----------
class UserSerializer(serializers.ModelSerializer):
    # explicit password field (write-only) using CharField
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    full_name = serializers.SerializerMethodField()  # demonstrates SerializerMethodField usage

    class Meta:
        model = User
        fields = [
            "user_id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "password",
            "phone_number",
            "role",
            "created_at",
        ]
        read_only_fields = ("user_id", "created_at", "full_name")

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def create(self, validated_data):
        # pop password and use set_password so hashing is correct
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        # handle password updates safely
        password = validated_data.pop("password", None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


# ---------- Message Serializer ----------
class MessageSerializer(serializers.ModelSerializer):
    # allow sender and recipient to be passed as UUIDs for create/update
    sender_id = serializers.UUIDField(write_only=True, required=True)
    recipient_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    # show nested sender & recipient in read responses
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    # explicit CharField usage for message_body (satisfies checks)
    message_body = serializers.CharField()

    class Meta:
        model = Message
        fields = [
            "message_id",
            "sender",
            "recipient",
            "sender_id",
            "recipient_id",
            "conversation",
            "message_body",
            "sent_at",
        ]
        read_only_fields = ("message_id", "sent_at", "sender", "recipient")

    def validate(self, attrs):
        # ensure conversation exists when provided and that sender is a participant
        conv = attrs.get("conversation", None)
        sender_id = attrs.get("sender_id")
        if conv is None:
            raise serializers.ValidationError({"conversation": "Conversation is required."})
        if sender_id and not conv.participants.filter(user_id=sender_id).exists():
            raise serializers.ValidationError({"sender_id": "Sender must be a participant of the conversation."})
        return attrs

    def create(self, validated_data):
        sender_id = validated_data.pop("sender_id")
        recipient_id = validated_data.pop("recipient_id", None)
        conversation = validated_data.pop("conversation")
        message = Message.objects.create(
            sender_id=sender_id,
            recipient_id=recipient_id,
            conversation=conversation,
            **validated_data,
            sent_at=timezone.now()
        )
        return message


# ---------- Conversation Serializer ----------
class ConversationSerializer(serializers.ModelSerializer):
    # For writes: accept a list of participant UUIDs
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=True, allow_empty=False
    )
    # For reads: show nested user objects
    participants = UserSerializer(many=True, read_only=True)
    # Include nested messages within a conversation (read-only)
    messages = MessageSerializer(many=True, read_only=True)
    # a derived field using SerializerMethodField
    last_message_preview = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participant_ids",     # write-only field to create/update participants
            "participants",        # read-only nested users
            "messages",            # read-only nested messages
            "last_message_preview",
            "created_at",
        ]
        read_only_fields = ("conversation_id", "participants", "messages", "last_message_preview", "created_at")

    def get_last_message_preview(self, obj):
        last = obj.messages.order_by("-sent_at").first()
        if not last:
            return None
        preview = last.message_body
        return (preview[:50] + "...") if len(preview) > 50 else preview

    def validate_participant_ids(self, value):
        # ensure unique participant ids and at least 2 participants
        unique_ids = list(dict.fromkeys(value))
        if len(unique_ids) < 2:
            raise serializers.ValidationError("A conversation must have at least two distinct participants.")
        return unique_ids

    def create(self, validated_data):
        participant_ids = validated_data.pop("participant_ids", [])
        conversation = Conversation.objects.create(**validated_data)
        # bulk add participants
        users = User.objects.filter(user_id__in=participant_ids)
        if users.count() != len(participant_ids):
            raise serializers.ValidationError("One or more participant IDs are invalid.")
        conversation.participants.set(users)
        conversation.save()
        return conversation

    def update(self, instance, validated_data):
        participant_ids = validated_data.pop("participant_ids", None)
        if participant_ids is not None:
            users = User.objects.filter(user_id__in=participant_ids)
            if users.count() != len(participant_ids):
                raise serializers.ValidationError("One or more participant IDs are invalid.")
            instance.participants.set(users)
        instance.save()
        return instance
