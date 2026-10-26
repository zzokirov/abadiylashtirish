"""Django Admin customization for Abadiy Xotira system.

Features:
- Direct QR code downloads (PNG 300DPI, SVG Laser, PDF Plaque) from admin list & detail.
- Bi-directional family relationship inlines (Parents & Children).
- Immutable audit log monitoring.
"""

from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Cemetery, DeceasedPerson, FamilyRelationship, QRCodeRecord, AuditLog
from .services import log_audit, get_client_ip


def qr_download_urls(token: str) -> tuple:
    return tuple(
        reverse('qr:download_qr', kwargs={'token': token, 'export_format': fmt})
        for fmt in ('png', 'svg', 'pdf')
    )


class ParentRelationshipInline(admin.TabularInline):
    """Marhumga ota yoki onasini biriktirish formasi."""
    model = FamilyRelationship
    fk_name = 'person'
    extra = 1
    verbose_name = "Ota / Ona yoki Turmush o‘rtog‘i"
    verbose_name_plural = "Ajdodlari va Turmush o‘rtog‘i (Biriktirish)"
    autocomplete_fields = ['related_person']


class ChildRelationshipInline(admin.TabularInline):
    """Marhumning farzandlarini ko'rish/biriktirish formasi."""
    model = FamilyRelationship
    fk_name = 'related_person'
    extra = 0
    verbose_name = "Farzandi"
    verbose_name_plural = "Avlodlari (Farzandlari)"
    autocomplete_fields = ['person']


@admin.register(DeceasedPerson)
class DeceasedPersonAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'gender',
        'birth_year_display',
        'death_year_display',
        'cemetery',
        'grave_number',
        'qr_download_buttons',
        'is_published',
    ]
    list_filter = ['cemetery', 'gender', 'is_published', 'is_archived', 'death_date']
    search_fields = ['last_name', 'first_name', 'middle_name', 'grave_number', 'qr_record__public_token']
    inlines = [ParentRelationshipInline, ChildRelationshipInline]
    readonly_fields = ['qr_preview_display', 'public_page_link', 'created_at', 'updated_at']

    fieldsets = (
        ("Asosiy Ma’lumotlar", {
            'fields': (
                ('last_name', 'first_name', 'middle_name'),
                ('gender', 'photo'),
                ('birth_date', 'death_date'),
            )
        }),
        ("Dafn Qilingan Joyi", {
            'fields': (
                ('cemetery', 'grave_number'),
            )
        }),
        ("Tarjimai holi va Xotiralar", {
            'fields': ('biography',)
        }),
        ("Doimiy QR-kod va Ommaviy Havola", {
            'fields': ('qr_preview_display', 'public_page_link'),
            'description': "QR-kod doimiydir va toshga o'yish uchun mo'ljallangan. Quyidagi formatlarda yuklab oling."
        }),
        ("Tizim Sozlamalari", {
            'fields': (
                ('is_published', 'is_archived'),
                ('created_at', 'updated_at'),
            ),
            'classes': ('collapse',)
        }),
    )

    def birth_year_display(self, obj):
        return obj.birth_date.year if obj.birth_date else "—"
    birth_year_display.short_description = "Tug‘ilgan yili"

    def death_year_display(self, obj):
        return obj.death_date.year
    death_year_display.short_description = "Vafot yili"

    def qr_download_buttons(self, obj):
        if not hasattr(obj, 'qr_record'):
            return "QR mavjud emas"
        png_url, svg_url, pdf_url = qr_download_urls(obj.qr_record.public_token)

        return format_html(
            '<a class="button" style="background:#1E3A2F;color:#fff;padding:3px 7px;border-radius:4px;font-size:11px;margin-right:2px;" href="{}" target="_blank">PNG</a>'
            '<a class="button" style="background:#2C5282;color:#fff;padding:3px 7px;border-radius:4px;font-size:11px;margin-right:2px;" href="{}" target="_blank">SVG</a>'
            '<a class="button" style="background:#744210;color:#fff;padding:3px 7px;border-radius:4px;font-size:11px;" href="{}" target="_blank">PDF</a>',
            png_url, svg_url, pdf_url
        )
    qr_download_buttons.short_description = "QR Eksport (Toshga)"

    def qr_preview_display(self, obj):
        if not hasattr(obj, 'qr_record'):
            return "QR yaratilmagan"
        token = obj.qr_record.public_token
        png_url, svg_url, pdf_url = qr_download_urls(token)

        return format_html(
            '<div style="display:flex;align-items:center;gap:20px;">'
            '  <div>'
            '    <p><b>Token:</b> <code>{}</code></p>'
            '    <p style="margin-top:10px;">'
            '      <a class="button" style="background:#1E3A2F;color:white;padding:8px 12px;text-decoration:none;border-radius:4px;" href="{}" target="_blank">📥 Yuqori Sifatli PNG (300 DPI)</a> '
            '      <a class="button" style="background:#2C5282;color:white;padding:8px 12px;text-decoration:none;border-radius:4px;" href="{}" target="_blank">📥 Lazer uchun SVG</a> '
            '      <a class="button" style="background:#744210;color:white;padding:8px 12px;text-decoration:none;border-radius:4px;" href="{}" target="_blank">📄 Tosh Ustasi uchun PDF Andoza</a>'
            '    </p>'
            '  </div>'
            '</div>',
            token, png_url, svg_url, pdf_url
        )
    qr_preview_display.short_description = "QR Kod Fayllari"

    def public_page_link(self, obj):
        if not hasattr(obj, 'qr_record'):
            return "—"
        url = f"{settings.FRONTEND_PUBLIC_BASE_URL}/{obj.qr_record.public_token}/"
        return format_html('<a href="{}" target="_blank" style="color:#1E3A2F;font-weight:bold;">{} ↗</a>', url, url)
    public_page_link.short_description = "Ommaviy Havola (Saytda ko‘rish)"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        log_audit(
            action=f"{'UPDATE' if change else 'CREATE'}_DECEASED: {obj.full_name}",
            user=request.user,
            ip_address=get_client_ip(request),
            details={'id': obj.id, 'full_name': obj.full_name, 'source': 'admin'},
        )

    def delete_model(self, request, obj):
        log_audit(
            action=f"DELETE_DECEASED: {obj.full_name}",
            user=request.user,
            ip_address=get_client_ip(request),
            details={'id': obj.id, 'full_name': obj.full_name, 'source': 'admin'},
        )
        super().delete_model(request, obj)


@admin.register(Cemetery)
class CemeteryAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'latitude', 'longitude', 'deceased_count']
    search_fields = ['name', 'address']

    def deceased_count(self, obj):
        return obj.deceased_persons.count()
    deceased_count.short_description = "Dafn etilganlar soni"


@admin.register(FamilyRelationship)
class FamilyRelationshipAdmin(admin.ModelAdmin):
    list_display = ['person', 'relationship_type', 'related_person', 'created_at']
    list_filter = ['relationship_type']
    search_fields = ['person__last_name', 'person__first_name', 'related_person__last_name', 'related_person__first_name']
    autocomplete_fields = ['person', 'related_person']


@admin.register(QRCodeRecord)
class QRCodeRecordAdmin(admin.ModelAdmin):
    list_display = ['public_token', 'deceased_person', 'is_active', 'created_at']
    search_fields = ['public_token', 'deceased_person__last_name', 'deceased_person__first_name']
    readonly_fields = ['public_token', 'created_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'action', 'user', 'ip_address']
    list_filter = ['action']
    search_fields = ['action', 'ip_address', 'details']
    readonly_fields = ['user', 'action', 'ip_address', 'details', 'timestamp']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# Django Admin bosh sahifasini Boshqaruv Markazi bilan boyitish.
# Statistikalar faqat bosh sahifada hisoblanadi (har bir admin sahifasida emas).
original_admin_index = admin.site.index


def custom_admin_index(request, extra_context=None):
    deceased_list = DeceasedPerson.objects.select_related('cemetery', 'qr_record').order_by('-created_at')
    context = {
        'total_deceased': deceased_list.count(),
        'total_published': deceased_list.filter(is_published=True, is_archived=False).count(),
        'total_cemeteries': Cemetery.objects.count(),
        'deceased_list': deceased_list,
        'cemeteries_list': Cemetery.objects.all(),
        'public_base_url': settings.FRONTEND_PUBLIC_BASE_URL,
        **(extra_context or {}),
    }
    return original_admin_index(request, extra_context=context)


admin.site.index = custom_admin_index
