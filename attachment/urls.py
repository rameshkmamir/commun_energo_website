from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import attachment_download

urlpatterns = [
                  path('attachments/<path:path>', attachment_download, name='attachment_download'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
