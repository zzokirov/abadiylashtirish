"""High-precision QR code generator and stone engraving export engine.

Features:
1. Error Correction Level H (30% damage recovery) - essential for outdoor
   granite/marble tombstone carvings and weathering.
2. Ultra-high resolution 300+ DPI monochrome PNG export.
3. Pure SVG vector export for direct laser engraving and CNC stone milling.
4. Printable A4/A5 Memorial Plaque PDF layout with person details.
"""

import io
from xml.sax.saxutils import escape

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.svg import SvgPathImage
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from django.conf import settings
from apps.core.models import DeceasedPerson

# Standart Helvetica shrifti o'zbekcha ‘ ’ belgilarini chiqara olmaydi (qora kvadrat bo'lib qoladi).
# ReportLab bilan birga keladigan Unicode TTF (Bitstream Vera) shriftlari ishlatiladi.
FONT_REGULAR = 'Vera'
FONT_BOLD = 'VeraBd'
FONT_ITALIC = 'VeraIt'

for _name in (FONT_REGULAR, FONT_BOLD, FONT_ITALIC):
    if _name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(_name, f'{_name}.ttf'))

# O'zbek lotin alifbosidagi ʻ va ʼ belgilari shriftda yo'q — vizual o'xshash ‘ ’ ga almashtiriladi
_APOSTROPHE_MAP = str.maketrans({'ʻ': '‘', 'ʼ': '’', '№': 'No'})


def pdf_text(value: str) -> str:
    """Matnni ReportLab Paragraph uchun xavfsiz holatga keltirish (&, <, > belgilari)."""
    return escape(str(value).translate(_APOSTROPHE_MAP))


class MemorialQRGenerator:
    """Qabr toshiga va ommaviy xotira sahifasiga mo'ljallangan QR generator."""

    def __init__(self, person: DeceasedPerson, base_url: str = None):
        self.person = person
        self.token = person.qr_record.public_token
        base = base_url or settings.FRONTEND_PUBLIC_BASE_URL
        # Diqqat: bu format o'zgarsa, toshga o'yilgan eski QR-kodlar bilan farq paydo bo'ladi
        self.target_url = f"{base.rstrip('/')}/{self.token}"

    def generate_high_res_png(self, box_size: int = 25, border: int = 4, inverted: bool = False) -> bytes:
        """Tosh o'yish va chop etish uchun 300+ DPI monoxrom PNG baytlarini qaytaradi.
        
        Args:
            box_size: Har bir nuqtaning piksel hajmi (katta o'lcham yuqori aniqlik beradi).
            border: Hoshiya kengligi.
            inverted: True bo'lsa qora fonda oq QR (qora granit uchun lazer gravyura).
        """
        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_H,
            box_size=box_size,
            border=border,
        )
        qr.add_data(self.target_url)
        qr.make(fit=True)

        fill_color = "white" if inverted else "black"
        back_color = "black" if inverted else "white"

        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', dpi=(300, 300))
        return buffer.getvalue()

    def generate_svg(self) -> str:
        """Lazer va frezer dastgohlari uchun vektorli SVG kodini qaytaradi."""
        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_H,
            box_size=10,
            border=4,
            image_factory=SvgPathImage
        )
        qr.add_data(self.target_url)
        qr.make(fit=True)
        img = qr.make_image()
        
        buffer = io.BytesIO()
        img.save(buffer)
        return buffer.getvalue().decode('utf-8')

    def generate_engraving_pdf_template(self) -> bytes:
        """Qabr tosh ustasi uchun A4 formatidagi rasmiy o'yma / metall lavha shabloni."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=20 * mm,
            rightMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            name='MemorialTitle',
            parent=styles['Normal'],
            fontName=FONT_BOLD,
            fontSize=16,
            leading=20,
            alignment=1, # Center
            textColor=colors.HexColor('#1E3A2F'),
        )

        name_style = ParagraphStyle(
            name='PersonName',
            parent=styles['Normal'],
            fontName=FONT_BOLD,
            fontSize=22,
            leading=26,
            alignment=1,
            textColor=colors.HexColor('#111111'),
        )

        years_style = ParagraphStyle(
            name='PersonYears',
            parent=styles['Normal'],
            fontName=FONT_REGULAR,
            fontSize=15,
            leading=20,
            alignment=1,
            textColor=colors.HexColor('#555555'),
        )

        note_style = ParagraphStyle(
            name='QRNote',
            parent=styles['Normal'],
            fontName=FONT_ITALIC,
            fontSize=11,
            leading=15,
            alignment=1,
            textColor=colors.HexColor('#222222'),
        )

        meta_style = ParagraphStyle(
            name='MetaStyle',
            parent=styles['Normal'],
            fontName=FONT_REGULAR,
            fontSize=10,
            leading=14,
            alignment=1,
            textColor=colors.HexColor('#666666'),
        )

        elements = []

        # Sarlavha
        elements.append(Paragraph("ABADIY XOTIRA — ELEKTRON SHAJARA TIZIMI", title_style))
        elements.append(Paragraph("Qabr toshiga tushirish uchun rasmiy QR-kod shabloni (Level H)", meta_style))
        elements.append(Spacer(1, 15 * mm))

        # Marhum ismi va yillari
        elements.append(Paragraph(pdf_text(self.person.full_name), name_style))
        elements.append(Spacer(1, 4 * mm))

        birth = self.person.birth_date.strftime("%d.%m.%Y") if self.person.birth_date else "—"
        death = self.person.death_date.strftime("%d.%m.%Y")
        elements.append(Paragraph(f"{birth} &nbsp;—&nbsp; {death}", years_style))
        elements.append(Spacer(1, 12 * mm))

        # QR kod rasmi (300 DPI PNG dan o'qib ReportLab rasmiga aylantiramiz)
        png_bytes = self.generate_high_res_png(box_size=10, border=2)
        qr_img_buffer = io.BytesIO(png_bytes)
        qr_image = RLImage(qr_img_buffer, width=70 * mm, height=70 * mm)
        qr_image.hAlign = 'CENTER'
        elements.append(qr_image)
        elements.append(Spacer(1, 8 * mm))

        # Qabr toshi ustidagi yo'riqnoma matni
        elements.append(Paragraph("Shajara va tarjimai holini o‘qish uchun telefon kamerasi orqali skanerlang", note_style))
        elements.append(Spacer(1, 4 * mm))
        elements.append(Paragraph(f"<b>URL:</b> {pdf_text(self.target_url)}", meta_style))

        location_parts = [self.person.cemetery.name if self.person.cemetery else "Noma’lum qabriston"]
        if self.person.grave_number:
            location_parts.append(f"Qabr raqami: {self.person.grave_number}")
        elements.append(Paragraph(" &nbsp;|&nbsp; ".join(pdf_text(p) for p in location_parts), meta_style))
        
        elements.append(Spacer(1, 15 * mm))

        # Tosh ustasi uchun texnik eslatma jadvali
        tech_info = [[cell.translate(_APOSTROPHE_MAP) for cell in row] for row in [
            ["Texnik parametrlar:", "Qiymat / Tavsiya:"],
            ["QR-kod standarti", "ISO/IEC 18004 (High Error Correction — 30%)"],
            ["Tavsiya etilgan o'lcham", "Kamida 50 mm x 50 mm (tosh yoki metall lavha)"],
            ["Chidamlilik", "30% sirt shikastlanganda ham o'qilish xususiyati saqlanadi"],
            ["Doimiylik", "Ushbu QR-kod o'zgarmasdir. Shajara ma'lumotlari serverda yangilanadi."],
        ]]
        t = Table(tech_info, colWidths=[65 * mm, 95 * mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F2F4F3')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#222222')),
            ('FONTNAME', (0, 0), (-1, -1), FONT_REGULAR),
            ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D0D4D2')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t)

        doc.build(elements)
        return buffer.getvalue()
