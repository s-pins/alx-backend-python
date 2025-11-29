
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory

# Task 0: Signal for User Notifications
@receiver(post_save, sender=Message)
def create_notification_on_new_message(sender, instance, created, **kwargs):
    """
    Automatically create a notification when a new message is created.
    """
    if created:
        Notification.objects.create(user=instance.receiver, message=instance)

# Task 1: Signal for Logging Message Edits
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Before a message is saved, check if its content has been modified.
    If so, log the original content to MessageHistory and mark the message as edited.
    """
    if instance.pk:  # Check if this is an update to an existing message
        try:
            original_message = Message.objects.get(pk=instance.pk)
            if original_message.content != instance.content:
                MessageHistory.objects.create(
                    message=original_message,
                    old_content=original_message.content
                )
                instance.edited = True
        except Message.DoesNotExist:
            # This can happen in rare cases, like if the message is being created with a specific pk
            pass

# Task 2: Signal for Deleting User-Related Data
@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    """
    When a user is deleted, clean up all their related data.
    This includes messages they sent or received, notifications, and message histories.
    """
    # Delete messages sent by the user
    Message.objects.filter(sender=instance).delete()
    
    # Delete messages received by the user
    Message.objects.filter(receiver=instance).delete()
    
    # Notifications for the user are automatically deleted due to the CASCADE on the user foreign key.
    # MessageHistories are also deleted via cascade from the Message model.
