
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .models import Message

@login_required
@require_POST
def create_message(request):
    """
    Creates a new message from the logged-in user to a specified receiver.
    This demonstrates setting the sender from the request user.
    """
    receiver_id = request.POST.get('receiver_id')
    content = request.POST.get('content')
    parent_id = request.POST.get('parent_message_id')

    if not receiver_id or not content:
        return HttpResponse("Receiver and content are required.", status=400)

    receiver = get_object_or_404(User, pk=receiver_id)
    parent_message = None
    if parent_id:
        parent_message = get_object_or_404(Message, pk=parent_id)

    message = Message.objects.create(
        sender=request.user,
        receiver=receiver,
        content=content,
        parent_message=parent_message
    )
    # Redirect to the message thread, assuming parent_id exists for replies
    # or a new conversation view for new messages.
    redirect_to = parent_message.get_absolute_url() if parent_message else '#'
    return redirect(redirect_to)


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
    # Get the top-level message in the thread, ensuring the user is part of the conversation
    q_filter = Q(pk=thread_id, parent_message__isnull=True) & (Q(sender=request.user) | Q(receiver=request.user))
    top_message = get_object_or_404(Message, q_filter)

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
    # Task 4: Optimize with .only() to retrieve only necessary fields.
    unread_messages = Message.unread.unread_for_user(request.user).select_related('sender').only(
        'id', 'content', 'timestamp', 'sender__username'
    )
    
    # Mark messages as read once they are viewed
    # In a real app, this might be done via an AJAX call or when a specific thread is opened
    # For simplicity, we'll just list them here.
    # unread_messages.update(read=True) 

    context = {
        'unread_messages': unread_messages,
    }
    return render(request, 'messaging/inbox.html', context)
