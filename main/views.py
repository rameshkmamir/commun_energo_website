import json
from urllib.parse import unquote_plus

from django.db.models import Q
from django.shortcuts import render, redirect

from messages_home.models import Conversation
from django.contrib.auth.models import User
from collections import defaultdict
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from django.http import HttpResponse


def index(request):
    user = request.user
    if user.is_authenticated and user.groups.filter(name='Обычные пользователи').exists():
        return redirect('conversations_list')
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
        date_filter = Q(created_at__gte=date_start) & Q(created_at__lte=date_end)
        conversations = conversations.filter(date_filter)
        context['date_start'] = date_start
        context['date_end'] = date_end
    if date_start and not (date_end):
        date_filter = Q(created_at__gte=date_start)
        conversations = conversations.filter(date_filter)
        context['date_start'] = date_start
    if date_end and not (date_start):
        date_filter = Q(created_at__lte=date_end)
        conversations = conversations.filter(date_filter)
        context['date_end'] = date_end

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
        return redirect(previous_page)

def report(request):
    users = User.objects.filter(groups__name__in=['Администратор', 'Поддержка'])

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
    doc = SimpleDocTemplate(response, pagesize=letter)

    elements = []

    for user in users:
        conversations = Conversation.objects.filter(user2=user)

        # Создание словаря для хранения данных по датам и статусам
        data_dict = defaultdict(lambda: [0, 0, 0])

        for conversation in conversations:
            date = conversation.created_at.date()
            status = conversation.status

            # Увеличение количества заявок по статусу для соответствующей даты
            if status == 'Активная':
                data_dict[date][0] += 1
            elif status == 'Отложена':
                data_dict[date][1] += 1
            elif status == 'Закрыта':
                data_dict[date][2] += 1

        # Создание таблицы данных
        table_data = [[f'Отчет для пользователя: {user.first_name} {user.last_name}']]
        table_data.append(['Дата', 'Активная', 'Отложена', 'Закрыта'])

        for date, counts in data_dict.items():
            row = [date, counts[0], counts[1], counts[2]]
            table_data.append(row)

        # Определение ширины столбцов
        table_width = doc.width
        column_widths = [table_width * 0.25, table_width * 0.25, table_width * 0.25, table_width * 0.25]

        # Создание таблицы для пользователя
        table = Table(table_data, colWidths=column_widths)
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Добавление границ ячеек
            ('SPAN', (0, 0), (-1, 0)),  # Объединение ячеек заголовка
        ])
        table.setStyle(style)

        elements.append(table)

    doc.build(elements)

    return response