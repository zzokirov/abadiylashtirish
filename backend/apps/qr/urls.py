from django.urls import path
from .views import QRCodeDownloadView

app_name = 'qr'

urlpatterns = [
    path('<str:token>/download/<str:export_format>/', QRCodeDownloadView.as_view(), name='download_qr'),
]
