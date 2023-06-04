from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('settings', views.settings, name='settings'),
    path('report', views.report, name='report'),
    path('report-xlsx', views.report_xlsx, name='report-xlsx')
]
