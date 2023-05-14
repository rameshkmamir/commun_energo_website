from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Conversation, Message, Attachment


class ConversationForm(forms.ModelForm):
  class Meta:
    model = Conversation
    fields = ['title']


class MessageForm(forms.ModelForm):
  class Meta:
    model = Message
    fields = ['text']

  text = forms.CharField(
    widget=forms.Textarea(
      attrs={
        'class': 'form-control',
        'rows': 3,
        'placeholder': 'Введите сообщение'
      }
    ),
    label=''
  )


class AttachmentForm(forms.ModelForm):
  class Meta:
    model = Attachment
    fields = ['file']

  def clean_file(self):
    file = self.cleaned_data['file']
    if file.size > 10485760:  # 10 MB
      raise ValidationError(_('File size must be under 10 MB'))
    return file
