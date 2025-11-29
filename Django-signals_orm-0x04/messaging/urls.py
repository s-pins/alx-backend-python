
from django.urls import path
from . import views

# In a real application, you would have better URL naming and structure
urlpatterns = [
    path('user/delete/', views.delete_user, name='delete_user'),
    path('thread/<int:thread_id>/', views.message_thread, name='message_thread'),
    path('inbox/', views.inbox, name='inbox'),
]
