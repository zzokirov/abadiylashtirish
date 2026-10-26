"""URL configuration for Abadiy Xotira project."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from apps.core.views import (
    MemorialPageView,
    AdminCreateDeceasedAction,
    AdminCreateRelationAction,
)

urlpatterns = [
    # Bosh sahifa va panel to'g'ridan-to'g'ri yangilangan Admin Panelga yo'naltiriladi
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    path('panel/', RedirectView.as_view(url='/admin/', permanent=False)),

    # Admin ichidagi tezkor qo'shish va shajara bog'lash amallari
    path('admin/quick-create-deceased/', AdminCreateDeceasedAction.as_view(), name='admin-quick-create-deceased'),
    path('admin/quick-create-relation/', AdminCreateRelationAction.as_view(), name='admin-quick-create-relation'),

    # Ommaviy doimiy QR sahifa: https://domain.uz/m/{token}/
    path('m/<str:token>/', MemorialPageView.as_view(), name='memorial-web-view'),

    # Django Admin paneli (To'liq zamonaviy Boshqaruv Markazi bilan boyitilgan)
    path('admin/', admin.site.urls),

    # REST API lar
    path('api/v1/', include('apps.core.urls')),
    path('api/v1/qr/', include('apps.qr.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Abadiy Xotira"
admin.site.site_title = "Abadiy Xotira Admin"
admin.site.index_title = "Elektron Shajara va Qabriston Boshqaruv Markazi"
