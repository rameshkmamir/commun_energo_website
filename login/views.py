from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.shortcuts import render, redirect

from .forms import CustomAuthenticationForm


def login_view(request):
  if request.method == 'POST':
    form = CustomAuthenticationForm(request, data=request.POST)
    if form.is_valid():
      username = form.cleaned_data.get('username')
      password = form.cleaned_data.get('password')
      user = authenticate(request, username=username, password=password)
      if user is not None:
        login(request, user)
        return redirect('home')
  else:
    form = CustomAuthenticationForm()
  return render(request, 'login/login.html', {'form': form})


def logout_view(request):
  logout(request)
  return redirect('login')
