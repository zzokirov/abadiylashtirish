"""URL routes for core application."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PublicDeceasedDetailView,
    PublicFamilyTreeView,
    AdminDeceasedViewSet,
    AdminCemeteryViewSet,
    AdminFamilyRelationshipViewSet,
)

router = DefaultRouter()
router.register(r'admin/deceased', AdminDeceasedViewSet, basename='admin-deceased')
router.register(r'admin/cemeteries', AdminCemeteryViewSet, basename='admin-cemeteries')
router.register(r'admin/relationships', AdminFamilyRelationshipViewSet, basename='admin-relationships')

urlpatterns = [
    # Ommaviy doimiy QR endpointlar
    path('public/deceased/<str:token>/', PublicDeceasedDetailView.as_view(), name='public-deceased-detail'),
    path('public/deceased/<str:token>/tree/', PublicFamilyTreeView.as_view(), name='public-deceased-tree'),

    # Admin boshqaruv API lari
    path('', include(router.urls)),
]
