
from django.db import models
from django.contrib.auth.models import User

# Task 4: Custom ORM Manager for Unread Messages
class UnreadMessagesManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(read=False)

    def unread_for_user(self, user):
        return self.get_queryset().filter(receiver=user)

# Task 0, 1, 3, 4: Message Model
class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Task 1: Field to track edits
    edited = models.BooleanField(default=False)
    
    # Task 3: Field for threaded conversations
    parent_message = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    # Task 4: Field to track read status
    read = models.BooleanField(default=False)

    objects = models.Manager()  # The default manager.
    unread = UnreadMessagesManager()  # The custom manager for unread messages.

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username} at {self.timestamp:%Y-%m-%d %H:%M}"

# Task 0: Notification Model
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username} about message from {self.message.sender.username}"

# Task 1: Message History Model
class MessageHistory(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-edited_at']

    def __str__(self):
        return f"History for message ID {self.message.pk} at {self.edited_at:%Y-%m-%d %H:%M}"

