from datetime import datetime, time
from time import sleep
from urllib.parse import unquote_plus
from django.forms.models import model_to_dict
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
import imghdr
from .forms import MessageForm, ConversationForm
from .models import Conversation, Message, Attachment

@login_required
def conversations_list(request):
    if request.method == 'POST':
        form = ConversationForm(request.POST)
        if form.is_valid():
            new_conversation = form.save(commit=False)
            new_conversation.user1 = request.user
            new_conversation.status = 'Активная'
            new_conversation.save()
            return JsonResponse({'url': reverse('conversation_detail', args=[new_conversation.id])})
        else:
            return JsonResponse({'error': form.errors})
    else:
        form = ConversationForm()

    user = request.user
    if user.is_authenticated and user.groups.filter(name='Обычные пользователи').exists():
        normal_users = User.objects.filter(
            groups__name='Обычные пользователи')
        conversations = Conversation.objects.filter(
            Q(user1__in=normal_users) | Q(user2__in=normal_users))
    else:
        # Формирование фильтрации запроса на основе GET-параметров
        conversations = Conversation.objects.all()
    number = request.GET.get('number')
    date = request.GET.get('date')
    status = request.GET.get('status')
    sender = request.GET.get('sender')
    recipient = request.GET.get('recipient')

    if number:
        number = int(number)
        conversations = conversations.filter(id__icontains=number)
    if date:
        date = datetime.strptime(date, '%Y-%m-%d').date()
        start_date = datetime.combine(date, time.min)
        end_date = datetime.combine(date, time.max)
        conversations = conversations.filter(
            created_at__gte=start_date, created_at__lt=end_date)
    if status:
        conversations = conversations.filter(status=status)
    if sender:
        sender = unquote_plus(sender)
        sender_parts = sender.split()
        if len(sender_parts) >= 2:
            sender_filter = Q(user1__first_name__icontains=sender_parts[0]) | Q(
                user1__last_name__icontains=sender_parts[1])
        else:
            sender_filter = Q(user1__first_name__icontains=sender) | Q(
                user1__last_name__icontains=sender)
        conversations = conversations.filter(sender_filter)

    if recipient:
        recipient_filter = Q(user2__first_name__icontains=recipient) | Q(
            user2__last_name__icontains=recipient)
        conversations = conversations.filter(recipient_filter)
    return render(request, 'messages_home/conversations_list.html', {
        'conversations': conversations
    })


@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation.objects.filter(Q(id=conversation_id)))
    messages = conversation.messages.all()
    attachments = Attachment.objects.filter(message__conversation=conversation)
    support_group = Group.objects.get(name='Поддержка')
    support_users = User.objects.filter(groups__name=support_group.name)
    
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            attachment = request.FILES.get('message_attachment')
            if attachment is not None:
                attachment = Attachment.objects.create(
                    file=attachment,
                    uploaded_by=request.user
                )
            message.attachment = attachment

            if request.user.groups.filter(name='Поддержка').exists():
                conversation.user2 = message.sender
            conversation.save()
            message.save()

            created_at = message.created_at
            formatted_date = created_at.strftime('%d %B %Y г. %H:%M')
            formatted_date = formatted_date.replace(
            formatted_date.split()[1],
            {
                "January": "января",
                "February": "февраля",
                "March": "марта",
                "April": "апреля",
                "May": "мая",
                "June": "июня",
                "July": "июля",
                "August": "августа",
                "September": "сентября",
                "October": "октября",
                "November": "ноября",
                "December": "декабря",
            }[formatted_date.split()[1]],)
            
            # сохраняем вложение в модель Attachment
            
            if message.attachment is not None:              
                message_data = {
                    'attachment': message.attachment.file.url,
                    'text': message.text,
                    'sender': message.sender.username,
                    'sender_first_name': message.sender.first_name,
                    'sender_last_name': message.sender.last_name,
                    'created_at': formatted_date,
                    'user': request.user.username,
                }
                print(message.sender.username)
            else:
                message_data = {
                    'text': message.text,
                    'sender': message.sender.username,
                    'sender_first_name': message.sender.first_name,
                    'sender_last_name': message.sender.last_name,
                    'created_at': formatted_date,
                    'user': request.user.username,
                }
            return JsonResponse({'message': message_data})
    else:
        form = MessageForm()

    context = {
        'conversation': conversation,
        'messages': messages,
        'form': form,
        'user': request.user,
        'support_users': support_users,
    }
    
    return render(request, 'messages_home/conversation_detail.html', context)


@login_required
def message_create(request):
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            data = {'is_valid': True, 'name': message.attachment.name,
                    'url': message.attachment.url}
        else:
            data = {'is_valid': False}
    else:
        data = {'is_valid': False}
    return JsonResponse(data)


@login_required
def conversation_ajax(request, pk):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == 'GET':
        conversation_id = pk
        conversation = Conversation.objects.get(id=conversation_id)
        messages = Message.objects.filter(
            conversation=conversation).order_by('-created_at')[:10]
        message_list = []
        for message in messages:
            message_list.append(
                {'text': message.text, 'created_at': message.created_at, 'sender': message.sender.username})
        return JsonResponse({'messages': message_list})
    else:
        return JsonResponse({'error': 'Invalid request'})


@login_required
def conversation_new(request):
    if request.method == 'POST':
        form = ConversationForm(request.POST)
        if form.is_valid():
            conversation = form.save(commit=False)
            conversation.user1 = request.user  # Устанавливаем user1
            conversation.save()
            return redirect('conversation_detail', conversation_id=conversation.id)
    else:
        form = ConversationForm()
    return render(request, 'messages_home/new_conversation.html', {'form': form})
