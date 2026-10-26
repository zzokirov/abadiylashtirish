"""API Views for public memorial pages and admin tree management.

Complies with:
- Strict Cache-Control: no-cache, no-store, must-revalidate on public endpoints.
- High security data masking for public view.
- Full DAG integrity verification.
"""

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.views.generic import View
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.exceptions import NotFound

from .models import Cemetery, DeceasedPerson, FamilyRelationship, RelationshipType
from .serializers import (
    CemeterySerializer,
    PublicDeceasedDetailSerializer,
    AdminDeceasedSerializer,
    FamilyRelationshipSerializer,
)
from .services import FamilyTreeService, log_audit, get_client_ip


NO_CACHE_HEADERS = {
    'Cache-Control': 'no-cache, no-store, must-revalidate, max-age=0',
    'Pragma': 'no-cache',
    'Expires': '0',
}


def apply_no_cache(response):
    """Brauzer va proksilar eski shajarani keshlab qolmasligi uchun sarlavhalar."""
    for header, value in NO_CACHE_HEADERS.items():
        response[header] = value
    return response


def published_persons():
    """Ommaga ochiq, faol QR-kodli marhumlar."""
    return DeceasedPerson.objects.select_related('cemetery', 'qr_record').filter(
        qr_record__is_active=True,
        is_published=True,
        is_archived=False,
    )


def validation_error_text(exc: ValidationError) -> str:
    return " ".join(exc.messages)


# ---------------------------------------------------------------------------
# Admin bosh sahifasidagi tezkor amallar (faqat xodimlar uchun)
# ---------------------------------------------------------------------------

@method_decorator([staff_member_required, require_POST], name='dispatch')
class AdminCreateDeceasedAction(View):
    """Admin paneldan tezkor yangi marhum kiritish amali."""

    def post(self, request):
        cemetery_id = request.POST.get('cemetery_id') or None
        person = DeceasedPerson(
            first_name=request.POST.get('first_name', '').strip(),
            last_name=request.POST.get('last_name', '').strip(),
            middle_name=request.POST.get('middle_name', '').strip(),
            birth_date=request.POST.get('birth_date') or None,
            death_date=request.POST.get('death_date') or None,
            gender=request.POST.get('gender', DeceasedPerson.GENDER_MALE),
            cemetery=Cemetery.objects.filter(pk=cemetery_id).first() if cemetery_id else None,
            grave_number=request.POST.get('grave_number', '').strip(),
            biography=request.POST.get('biography', '').strip(),
            is_published=True,
        )
        try:
            # save() ichida full_clean() barcha maydon va sana qoidalarini tekshiradi
            person.save()
        except ValidationError as exc:
            messages.error(request, f"Marhum qo‘shilmadi: {validation_error_text(exc)}")
            return redirect('admin:index')

        log_audit(
            action=f"CREATE_DECEASED: {person.full_name}",
            user=request.user,
            ip_address=get_client_ip(request),
            details={'id': person.id, 'full_name': person.full_name},
        )
        messages.success(request, f"«{person.full_name}» muvaffaqiyatli qo‘shildi va unga doimiy QR-kod yaratildi.")
        return redirect('admin:index')


@method_decorator([staff_member_required, require_POST], name='dispatch')
class AdminCreateRelationAction(View):
    """Admin paneldan shajara ota-ona / turmush o'rtoq bog'lash amali."""

    def post(self, request):
        child_id = request.POST.get('child_id')
        parent_id = request.POST.get('parent_id')
        rel_type = request.POST.get('relationship_type', RelationshipType.PARENT)

        if not (child_id and parent_id):
            messages.error(request, "Ikkala shaxsni ham tanlang.")
            return redirect('admin:index')

        rel = FamilyRelationship(
            person=get_object_or_404(DeceasedPerson, pk=child_id),
            related_person=get_object_or_404(DeceasedPerson, pk=parent_id),
            relationship_type=rel_type,
        )
        try:
            rel.save()
        except ValidationError as exc:
            messages.error(request, f"Aloqa saqlanmadi: {validation_error_text(exc)}")
            return redirect('admin:index')

        log_audit(
            action=f"CREATE_RELATIONSHIP: {rel}",
            user=request.user,
            ip_address=get_client_ip(request),
            details={'person_id': rel.person_id, 'related_id': rel.related_person_id, 'type': rel.relationship_type},
        )
        messages.success(request, f"Shajara aloqasi saqlandi: {rel}")
        return redirect('admin:index')


# ---------------------------------------------------------------------------
# Ommaviy sahifa va API
# ---------------------------------------------------------------------------

class MemorialPageView(View):
    """Qabr toshidagi QR-kod skanerlanganda to'g'ridan-to'g'ri ochiladigan to'liq interfaol sahifa."""

    @method_decorator(never_cache)
    def get(self, request, token: str):
        person = get_object_or_404(published_persons(), qr_record__public_token=token)
        return apply_no_cache(render(request, 'memorial.html', {
            'token': token,
            'person': person,
            'map': cemetery_map_context(person.cemetery),
        }))


def cemetery_map_context(cemetery):
    """Xarita havolalari uchun nuqtali (lokalizatsiyasiz) koordinatalar."""
    if not cemetery or cemetery.latitude is None or cemetery.longitude is None:
        return None
    lat, lon = float(cemetery.latitude), float(cemetery.longitude)
    return {
        'lat': f"{lat:.6f}",
        'lon': f"{lon:.6f}",
        'bbox': f"{lon - 0.006:.6f},{lat - 0.004:.6f},{lon + 0.006:.6f},{lat + 0.004:.6f}",
    }


class PublicDeceasedDetailView(APIView):
    """Doimiy QR-kod skanerlanganda ochiladigan asosiy ommaviy endpoint.

    Talab: Brauzerlar eski shajara yoki ma'lumotni keshlab qolmasligi uchun
    Cache-Control: no-cache, no-store, must-revalidate qat'iy o'rnatiladi.
    """
    permission_classes = [AllowAny]

    @method_decorator(never_cache)
    def get(self, request, token: str):
        person = published_persons().filter(qr_record__public_token=token).first()
        if person is None:
            raise NotFound("Ushbu QR-kodga tegishli marhum sahifasi topilmadi yoki faol emas.")

        serializer = PublicDeceasedDetailSerializer(person, context={'request': request})
        return apply_no_cache(Response(serializer.data, status=status.HTTP_200_OK))


class PublicFamilyTreeView(APIView):
    """Marhumning butun ajdodlari va avlodlari shajarasi (Dinamik).

    Qabr toshidagi QR o'zgarmaydi, ushbu endpoint esa doimo eng oxirgi
    qo'shilgan ota-onalar, bobolar va farzandlar holatini chiqarib beradi.
    """
    permission_classes = [AllowAny]

    @method_decorator(never_cache)
    def get(self, request, token: str):
        person = published_persons().filter(qr_record__public_token=token).first()
        if person is None:
            raise NotFound("Shajara topilmadi.")

        tree_data = FamilyTreeService(focal_person=person).build_full_tree()
        return apply_no_cache(Response(tree_data, status=status.HTTP_200_OK))


# ---------------------------------------------------------------------------
# Admin REST API
# ---------------------------------------------------------------------------

class AuditedModelViewSet(viewsets.ModelViewSet):
    """Yaratish, tahrirlash va o'chirishni audit jurnaliga yozuvchi ViewSet."""
    permission_classes = [IsAdminUser]
    audit_name = 'OBJECT'

    def audit_details(self, instance) -> dict:
        return {'id': instance.pk, 'repr': str(instance)}

    def _audit(self, verb: str, instance) -> None:
        log_audit(
            action=f"{verb}_{self.audit_name}: {instance}",
            user=self.request.user,
            ip_address=get_client_ip(self.request),
            details=self.audit_details(instance),
        )

    def perform_create(self, serializer):
        self._audit('CREATE', serializer.save())

    def perform_update(self, serializer):
        self._audit('UPDATE', serializer.save())

    def perform_destroy(self, instance):
        self._audit('DELETE', instance)
        instance.delete()


class AdminDeceasedViewSet(AuditedModelViewSet):
    """Administratorlar uchun marhumni yaratish, tahrirlash va ro'yxatini ko'rish."""
    queryset = DeceasedPerson.objects.select_related('cemetery', 'qr_record').all()
    serializer_class = AdminDeceasedSerializer
    audit_name = 'DECEASED'

    def audit_details(self, instance) -> dict:
        return {'id': instance.id, 'full_name': instance.full_name}


class AdminCemeteryViewSet(AuditedModelViewSet):
    """Administratorlar uchun qabristonlar boshqaruvi."""
    queryset = Cemetery.objects.all()
    serializer_class = CemeterySerializer
    audit_name = 'CEMETERY'


class AdminFamilyRelationshipViewSet(AuditedModelViewSet):
    """Qarindoshlik aloqalarini biriktirish va o'chirish."""
    queryset = FamilyRelationship.objects.select_related('person', 'related_person').all()
    serializer_class = FamilyRelationshipSerializer
    audit_name = 'RELATIONSHIP'

    def audit_details(self, instance) -> dict:
        return {
            'person_id': instance.person_id,
            'related_id': instance.related_person_id,
            'type': instance.relationship_type,
        }
