from django.shortcuts import render
import json
from messages_home.models import Conversation
from django.db.models import Count
from urllib.parse import unquote_plus
from django.db.models import Q
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect

def index(request):
    user = request.user
    if user.is_authenticated and user.groups.filter(name='Обычные пользователи').exists():
          return redirect ('conversations_list')
    if user.is_authenticated and user.groups.filter(name='Поддержка').exists():
        conversations = Conversation.objects.filter(Q(user2__username__icontains=user))
    else: 
        conversations = Conversation.objects.all()

    data = {
        'labels': [],
        'datasets': [
            {'label': 'Активная', 'data': []},
            {'label': 'Закрыта', 'data': []},
            {'label': 'Отложена', 'data': []}
        ]
    }
    
    recipient = request.GET.get('user_name')
    date_start = request.GET.get('date_start')
    date_end = request.GET.get('date_end')
    context = {}
    if recipient:
        recipient = unquote_plus(recipient)
        recipient_parts = recipient.split()
        if len(recipient_parts) >= 2:
            recipient_filter = Q(user2__first_name__icontains=recipient_parts[0]) | Q(
                user2__last_name__icontains=recipient_parts[1])
        else:
            recipient_filter = Q(user2__first_name__icontains=recipient) | Q(
                user2__last_name__icontains=recipient)
        conversations = conversations.filter(recipient_filter)
        context['recipient'] = recipient
    if date_start and date_end:
        date_filter =  Q(created_at__gte=date_start) & Q(created_at__lte=date_end)
        conversations = conversations.filter(date_filter) 
    if date_start and not(date_end):
        date_filter =  Q(created_at__gte=date_start)
        conversations = conversations.filter(date_filter)
    if date_end and not(date_start):
        date_filter =  Q(created_at__lte=date_end)
        conversations = conversations.filter(date_filter)


    # Формирование данных для графика
    for conversation in conversations:
        created_at = conversation.created_at.date().strftime('%Y-%m-%d')
        data['labels'].append(created_at)
        if conversation.status == 'Активная':
            data['datasets'][0]['data'].append(created_at)
        elif conversation.status == 'Закрыта':
            data['datasets'][1]['data'].append(created_at)
        elif conversation.status == 'Отложена':
            data['datasets'][2]['data'].append(created_at)

    context.update({
        'data': json.dumps(data),
        'date_end': date_end,
        'date_start': date_start
    })
    return render(request, "main/index.html", context=context)

def settings(request):
  user = request.user

  data = {
    "title": "Настройки",
  }
  if user.is_authenticated and user.groups.filter(name='Администратор').exists():
    return render(request, "main/settings.html", data)
  else:
    previous_page = request.META.get('HTTP_REFERER')
    return redirect (previous_page)
  
  