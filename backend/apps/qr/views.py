"""API endpoints for downloading production-grade QR code assets."""

from django.http import HttpResponse, Http404
from django.utils.http import content_disposition_header
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from apps.core.models import DeceasedPerson
from .generator import MemorialQRGenerator


class QRCodeDownloadView(APIView):
    """Qabr toshiga qo'yish uchun yuqori sifatli QR kodlarni eksport qilish (Faqat adminlar uchun)."""
    permission_classes = [IsAdminUser]

    def _get_person(self, token: str) -> DeceasedPerson:
        try:
            return DeceasedPerson.objects.select_related('qr_record', 'cemetery').get(qr_record__public_token=token)
        except DeceasedPerson.DoesNotExist:
            raise Http404("Marhum yoki uning QR yozuvi topilmadi.")

    def get(self, request, token: str, export_format: str):
        person = self._get_person(token)
        generator = MemorialQRGenerator(person)

        export_format = export_format.lower()
        filename_prefix = f"QR_{person.last_name}_{person.first_name}_{token[:8]}"

        if export_format == 'png':
            inverted = request.query_params.get('inverted', 'false').lower() == 'true'
            image_data = generator.generate_high_res_png(box_size=20, border=4, inverted=inverted)
            response = HttpResponse(image_data, content_type='image/png')
            suffix = "_inverted" if inverted else ""
            response['Content-Disposition'] = content_disposition_header(True, f"{filename_prefix}{suffix}.png")
            return response

        elif export_format == 'svg':
            svg_data = generator.generate_svg()
            response = HttpResponse(svg_data, content_type='image/svg+xml')
            response['Content-Disposition'] = content_disposition_header(True, f"{filename_prefix}.svg")
            return response

        elif export_format == 'pdf':
            pdf_data = generator.generate_engraving_pdf_template()
            response = HttpResponse(pdf_data, content_type='application/pdf')
            response['Content-Disposition'] = content_disposition_header(True, f"{filename_prefix}_plaque.pdf")
            return response

        return HttpResponse("Noto‘g‘ri format. Mavjud formatlar: png, svg, pdf", status=400)
