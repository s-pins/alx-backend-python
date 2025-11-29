
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification

class SignalsTestCase(TestCase):
    def setUp(self):
        """Set up two users for testing."""
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')

    def test_notification_created_on_new_message(self):
        """
        Test that a Notification is automatically created when a new Message is sent.
        """
        # Check that no notifications exist initially for user2
        self.assertEqual(Notification.objects.filter(user=self.user2).count(), 0)

        # Create a new message from user1 to user2
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello, this is a test message!"
        )

        # Check that one notification now exists for user2
        self.assertEqual(Notification.objects.filter(user=self.user2).count(), 1)

        # Verify the notification details
        notification = Notification.objects.get(user=self.user2)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.is_read)
