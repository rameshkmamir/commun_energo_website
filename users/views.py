from urllib.parse import unquote_plus

from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models import Subquery, OuterRef
from django.shortcuts import render

from messages_home.models import Conversation, Message


def users(request):
    users = User.objects.all()
    conversations = Conversation.objects.all()

    if request.method == 'GET':
        user_name = request.GET.get('username')
        user_access = request.GET.get('useraccess')
        context = {}
        if user_name:
            user_name = unquote_plus(user_name)
            user_name_parts = user_name.split()
            if len(user_name_parts) >= 2:
                user_name_filter = Q(first_name__icontains=user_name_parts[0]) | Q(
                    last_name__icontains=user_name_parts[1])
            else:
                user_name_filter = Q(first_name__icontains=user_name) | Q(
                    last_name__icontains=user_name)
            context['user_name'] = user_name
            users = users.filter(user_name_filter)
        if user_access:
            user_access = unquote_plus(user_access)
            user_access_filter = Q(groups__name__icontains=user_access)
            users = users.filter(user_access_filter)
            context['user_access'] = user_access
    conversations = conversations.annotate(
        latest_message_time=Subquery(
            Message.objects.filter(conversation=OuterRef('pk')).values('created_at').order_by('-created_at')[:1]
        )).order_by('-latest_message_time')
    context.update({
        'users': users,
        'conversations': conversations,
    })

    return render(request, 'users/users.html', context=context)
