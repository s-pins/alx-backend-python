
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .models import Message

# Task 2: View for Deleting a User Account
@login_required
@require_POST
def delete_user(request):
    """
    Deletes the currently logged-in user's account and all their related data.
    The actual data cleanup is handled by the post_delete signal on the User model.
    """
    user = request.user
    user.delete()
    return redirect('home') # Assuming you have a 'home' URL name to redirect to after deletion

# Task 3 & 5: View for Threaded Conversations with Caching and ORM optimization
@login_required
@cache_page(60) # Task 5: Cache this view for 60 seconds
def message_thread(request, thread_id):
    """
    Displays a threaded conversation, optimizing queries using select_related and prefetch_related.
    """
    # Get the top-level message in the thread
    top_message = get_object_or_404(Message, pk=thread_id, parent_message__isnull=True)

    # Task 3: Use prefetch_related and select_related for optimization
    # Efficiently fetch the message and all its replies, along with sender/receiver details.
    # This avoids the N+1 query problem.
    conversation = Message.objects.filter(pk=top_message.pk).prefetch_related(
        'replies__sender', 
        'replies__receiver'
    ).select_related('sender', 'receiver').first()
    
    # Example of using the custom manager from Task 4
    unread_count = Message.unread.unread_for_user(request.user).count()

    context = {
        'conversation': conversation,
        'unread_count': unread_count,
    }
    
    return render(request, 'messaging/thread.html', context)

# A simple view to demonstrate the custom manager
@login_required
def inbox(request):
    """
    Displays a user's unread messages using the custom manager.
    """
    unread_messages = Message.unread.unread_for_user(request.user).select_related('sender')
    
    # Mark messages as read once they are viewed
    # In a real app, this might be done via an AJAX call or when a specific thread is opened
    # For simplicity, we'll just list them here.
    # unread_messages.update(read=True) 

    context = {
        'unread_messages': unread_messages,
    }
    return render(request, 'messaging/inbox.html', context)
