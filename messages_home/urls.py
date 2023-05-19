from django.urls import path

from . import views
from .views import conversation_detail

urlpatterns = [
  path('', views.conversations_list, name='conversations_list'),
  path('conversations/<int:conversation_id>/', conversation_detail, name='conversation_detail'),
  path('conversations/<int:conversation_id>/update-conversation-user/', views.update_conversation_user, name='update_conversation_user'),
  path('conversations/<int:conversation_id>/update-conversation-status/', views.update_conversation_status, name='update_conversation_status'),
  path('conversations/<int:pk>/ajax/', views.conversation_ajax, name='conversations_ajax'),
  path('messages/<int:pk>/', views.message_create, name='message_create'),
]
