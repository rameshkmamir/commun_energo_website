from django.shortcuts import render
import json
from messages_home.models import Conversation
from django.db.models import Count

def index(request):
    # Получение данных из базы данных
    conversations = Conversation.objects.all()
    data = {
        'labels': [],
        'datasets': [
            {'label': 'Активная', 'data': []},
            {'label': 'Закрыта', 'data': []},
            {'label': 'Отложена', 'data': []}
        ]
    }
    
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

    print(data)
    return render(request, "main/index.html", {"data": json.dumps(data)})

def settings(request):
  data = {
    "title": "Настройки",
  }
  return render(request, "main/settings.html", data)