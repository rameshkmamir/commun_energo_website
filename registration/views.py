from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect

from .forms import CustomUserCreationForm


def register(request):
  if request.method == 'POST':
    form = CustomUserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      group = Group.objects.get(name='Обычные пользователи')
      user.groups.add(group)
      login(request, user)
      return redirect('home')
  else:
    form = CustomUserCreationForm()
  return render(request, 'registration/register.html', {'form': form})
