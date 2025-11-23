from rest_framework import permissions
from .models import Conversation

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it and its messages.
    """
    def has_permission(self, request, view):
        # Allow read-only access for anyone (authenticated or not) for safe methods at the list level.
        # But we also need to ensure the user is authenticated for any interaction with the API.
        # This will be handled by returning request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Check if the user is a participant for the specific object (Conversation or Message)
        is_participant = False
        if isinstance(obj, Conversation):
            is_participant = request.user in obj.participants.all()
        elif hasattr(obj, 'conversation'): # This is for Message objects
            is_participant = request.user in obj.conversation.participants.all()
        
        # If it's a safe method (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return is_participant
        
        # For non-safe methods (PUT, PATCH, POST, DELETE), only allow if the user is a participant.
        return is_participant