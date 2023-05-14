import os

from django.conf import settings
from django.http import HttpResponse, Http404


def attachment_download(request, path):
  # Получаем полный путь к файлу вложения
  file_path = os.path.join(settings.MEDIA_ROOT, 'attachments', path)

  # Проверяем, существует ли файл
  if os.path.exists(file_path):
    # Открываем файл и передаем его содержимое в HttpResponse
    with open(file_path, 'rb') as f:
      response = HttpResponse(f.read(), content_type='application/octet-stream')
      response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
      return response
  else:
    # Если файл не существует, выбрасываем исключение Http404
    raise Http404('File not found')
