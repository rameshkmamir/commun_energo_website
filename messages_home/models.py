from django.contrib.auth import get_user_model
from django.db import models
import imghdr

User = get_user_model()


class Conversation(models.Model):
  STATUS_CHOICES = [
    ('active', 'Активная'),
    ('closed', 'Закрыта'),
    ('snoozed', 'Отложена'),
  ]
  user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_started')
  user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_involved', null=True)

  title = models.CharField(max_length=50)
  created_at = models.DateTimeField(auto_now_add=True)
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Активная')

  class Meta:
    verbose_name_plural = 'Диалоги'
    verbose_name = 'Диалог'
    ordering = ['-created_at']

  def __str__(self):
    return f"{self.user1} - {self.user2}"

class Attachment(models.Model):
  file = models.FileField(upload_to='attachments/')
  uploaded_at = models.DateTimeField(auto_now_add=True)
  uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

  class Meta:
    verbose_name_plural = 'Вложения'
    verbose_name = 'Вложение'
  
  def is_committed(self):
        return bool(self.pk)


class Message(models.Model):
  text = models.TextField()
  conversation = models.ForeignKey(
    Conversation, related_name='messages', on_delete=models.CASCADE)
  sender = models.ForeignKey(
    User, related_name='messages', on_delete=models.CASCADE)
  created_at = models.DateTimeField(auto_now_add=True)
  attachment = models.ForeignKey(Attachment, on_delete=models.CASCADE, null=True, blank=True)

  class Meta:
    ordering = ('created_at',)
    verbose_name = 'Сообщение'
    verbose_name_plural = 'Сообщения'

  def __str__(self):
    return f'Conversation #{self.conversation.id} Message #{self.id}'



