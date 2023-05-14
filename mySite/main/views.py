from django.shortcuts import render


# Create your views here.
def index(request):
  data = {
    'title': 'Главная страница',
  }
  return render(request, 'main/index.html', data)


def settings(request):
  data = {
    'title': 'Настройки',
  }
  return render(request, 'main/settings.html', data)