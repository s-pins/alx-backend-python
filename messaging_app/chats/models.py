import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# ---------- User Model ----------
class User(AbstractUser):
    """Custom user model extending AbstractUser"""
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, null=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest')
    created_at = models.DateTimeField(default=timezone.now)

    # Optional: remove unused fields from AbstractUser if needed
    username = None
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


# ---------- Conversation Model ----------
class Conversation(models.Model):
    """Represents a chat conversation between multiple users"""
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Conversation {self.conversation_id}"


# ---------- Message Model ----------
class Message(models.Model):
    """Represents a message sent by a user in a conversation"""
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    message_body = models.TextField(null=False)
    sent_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Message {self.message_id} from {self.sender.email}"
