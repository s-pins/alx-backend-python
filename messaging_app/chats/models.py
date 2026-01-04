import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# ---------- User Model ----------
class User(AbstractUser):
    """Custom user model extending AbstractUser"""
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # The next two lines are redundant, as AbstractUser already defines these
    # first_name = models.CharField(max_length=30, null=False) 
    # last_name = models.CharField(max_length=30, null=False)

    email = models.EmailField(unique=True, db_index=True)  # indexed
    password = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest')
    created_at = models.DateTimeField(default=timezone.now)

    # Note: AbstractUser already defines username, first_name, last_name, email, 
    # is_staff, is_active, is_superuser, last_login, date_joined, password, 
    # groups, and user_permissions.

    # Define groups and user_permissions with unique related_name to avoid clashes
    # These fields are required when customizing the User model.
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=('groups'),
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="chat_user_groups",
        related_query_name="chat_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=('user permissions'),
        blank=True,
        help_text=('Specific permissions for this user.'),
        related_name="chat_user_permissions",
        related_query_name="chat_user",
    )
    
    # remove unused fields from AbstractUser if needed
    username = None
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name'] # Note: AbstractUser already has these fields

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    

# ---------- Conversation Model ----------
class Conversation(models.Model):
    """Model representing a conversation between users."""
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        participant_names = ", ".join([str(user) for user in self.participants.all()])
        return f"Conversation {self.conversation_id} between {participant_names}"
    

# ---------- Message Model ----------
class Message(models.Model):
    """Model representing a message in a conversation."""
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    message_body = models.TextField(NOT NULL)
    sent_at = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message {self.message_id} from {self.sender} at {self.timestamp}"
