from django.contrib import admin

from .models import Conversation, Attachment, Message

admin.site.register(Conversation)
admin.site.register(Attachment)
admin.site.register(Message)
