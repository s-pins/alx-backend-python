
from django.contrib import admin
from .models import Message, Notification, MessageHistory

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp', 'read', 'edited')
    list_filter = ('timestamp', 'read', 'edited')
    search_fields = ('content', 'sender__username', 'receiver__username')
    raw_id_fields = ('sender', 'receiver', 'parent_message')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_summary', 'created_at', 'is_read')
    list_filter = ('created_at', 'is_read')
    search_fields = ('user__username',)
    raw_id_fields = ('user', 'message')

    def message_summary(self, obj):
        return f"From {obj.message.sender} to {obj.message.receiver}"
    message_summary.short_description = 'Message'

@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ('message', 'edited_at')
    search_fields = ('message__id',)
    raw_id_fields = ('message',)
