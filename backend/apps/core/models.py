"""Database models for Abadiy Xotira system.

Includes:
- Cemetery
- DeceasedPerson
- FamilyRelationship
- QRCodeRecord
- AuditLog
"""

import secrets
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Cemetery(models.Model):
    """Qabriston modeli."""
    name = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name="Qabriston nomi"
    )
    address = models.CharField(
        max_length=500,
        verbose_name="Manzili"
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Kenglik (Latitude)"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Uzunlik (Longitude)"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Tavsifi / Tarixi"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Yaratilgan vaqti"
    )

    class Meta:
        verbose_name = "Qabriston"
        verbose_name_plural = "Qabristonlar"
        ordering = ['name']

    def __str__(self):
        return self.name


class DeceasedPerson(models.Model):
    """Marhum (vafot etgan shaxs) modeli.
    
    Qoidalar:
    - Faqat marhumlar kiritiladi.
    - death_date majburiy.
    - birth_date mavjud bo'lsa, birth_date <= death_date bo'lishi shart.
    - Kelajakdagi vafot sanalari rad etiladi.
    """
    GENDER_MALE = 'MALE'
    GENDER_FEMALE = 'FEMALE'
    GENDER_CHOICES = [
        (GENDER_MALE, 'Erkak'),
        (GENDER_FEMALE, 'Ayol'),
    ]

    first_name = models.CharField(
        max_length=100,
        verbose_name="Ismi"
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name="Familiyasi"
    )
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Otasining ismi"
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Tug‘ilgan sanasi"
    )
    death_date = models.DateField(
        verbose_name="Vafot etgan sanasi"
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default=GENDER_MALE,
        verbose_name="Jinsi"
    )
    photo = models.ImageField(
        upload_to='photos/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Fotosurati"
    )
    biography = models.TextField(
        blank=True,
        verbose_name="Tarjimai holi va ibratli xotiralari"
    )
    cemetery = models.ForeignKey(
        Cemetery,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deceased_persons',
        verbose_name="Dafn etilgan qabriston"
    )
    grave_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Qabr / Sektor raqami"
    )
    is_published = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Ommaga ochiq"
    )
    is_archived = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Arxivlangan"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Yozuv yaratilgan vaqti"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Oxirgi tahrirlash"
    )

    class Meta:
        verbose_name = "Marhum"
        verbose_name_plural = "Marhumlar"
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['is_published', 'is_archived']),
            models.Index(fields=['death_date']),
        ]
        ordering = ['-death_date']

    @property
    def full_name(self) -> str:
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)

    @property
    def age_at_death(self):
        """Necha yil umr ko'rgani (tug'ilgan sana noma'lum bo'lsa None)."""
        if not (self.birth_date and self.death_date):
            return None
        b, d = self.birth_date, self.death_date
        return d.year - b.year - ((d.month, d.day) < (b.month, b.day))

    def clean(self):
        super().clean()
        today = timezone.now().date()

        if self.death_date and self.death_date > today:
            raise ValidationError({
                'death_date': "Vafot sanasi kelajakdagi sana bo‘lishi mumkin emas."
            })

        if self.birth_date:
            if self.birth_date > today:
                raise ValidationError({
                    'birth_date': "Tug‘ilgan sana kelajakdagi sana bo‘lishi mumkin emas."
                })
            if self.death_date and self.birth_date > self.death_date:
                raise ValidationError({
                    'birth_date': "Tug‘ilgan sana vafot sanasidan keyin bo‘lishi mumkin emas."
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        is_new = self.pk is None
        super().save(*args, **kwargs)
        # Har bir yangi yaratilgan marhum uchun avtomatik tarzda QR-kod rekordi shakllantiriladi
        if is_new and not hasattr(self, 'qr_record'):
            QRCodeRecord.objects.create(deceased_person=self)

    def __str__(self):
        return f"{self.full_name} ({self.birth_date.year if self.birth_date else '?'} - {self.death_date.year})"


class RelationshipType(models.TextChoices):
    PARENT = 'PARENT', 'Ota / Ona'
    SPOUSE = 'SPOUSE', 'Turmush o‘rtog‘i'


class FamilyRelationship(models.Model):
    """Qarindoshlik aloqasi modeli.
    
    Qoidalar:
    - person: Shaxs (farzand yoki turmush o'rtoqlardan biri).
    - related_person: Bog'langan shaxs (PARENT bo'lsa person'ning ota yoki onasi; SPOUSE bo'lsa jufti).
    - Shaxs o'ziga o'zi qarindosh bo'la olmaydi.
    - Ajdod-avlod sikllari (DAG) qat'iy taqiqlanadi (services.py orqali tekshiriladi).
    """
    person = models.ForeignKey(
        DeceasedPerson,
        on_delete=models.CASCADE,
        related_name='parent_relationships',
        verbose_name="Farzand / Shaxs"
    )
    related_person = models.ForeignKey(
        DeceasedPerson,
        on_delete=models.CASCADE,
        related_name='child_relationships',
        verbose_name="Ota/Ona yoki Turmush o‘rtog‘i"
    )
    relationship_type = models.CharField(
        max_length=20,
        choices=RelationshipType.choices,
        default=RelationshipType.PARENT,
        verbose_name="Aloqa turi"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Biriktirilgan vaqti"
    )

    class Meta:
        verbose_name = "Qarindoshlik aloqasi"
        verbose_name_plural = "Qarindoshlik aloqalari"
        constraints = [
            models.UniqueConstraint(
                fields=['person', 'related_person', 'relationship_type'],
                name='unique_person_related_relationship'
            ),
            models.CheckConstraint(
                condition=~models.Q(person=models.F('related_person')),
                name='prevent_self_relationship'
            )
        ]
        indexes = [
            models.Index(fields=['person', 'relationship_type']),
            models.Index(fields=['related_person', 'relationship_type']),
        ]

    def clean(self):
        super().clean()
        if self.person_id and self.related_person_id:
            if self.person_id == self.related_person_id:
                raise ValidationError(
                    "Shaxs o‘ziga o‘zi ota/ona yoki turmush o‘rtoq qilib biriktirilishi mumkin emas!"
                )

            # Sikl tekshiruvi: faqat PARENT munosabatida chaqiriladi
            if self.relationship_type == RelationshipType.PARENT:
                from .services import validate_no_ancestry_cycle
                validate_no_ancestry_cycle(
                    child_id=self.person_id,
                    parent_id=self.related_person_id
                )

                # Biologik cheklov: Bir bolada maksimal 1 ta erkak ota va 1 ta ayol ona bo'lishi mumkin
                existing_parents = FamilyRelationship.objects.filter(
                    person=self.person,
                    relationship_type=RelationshipType.PARENT
                ).exclude(pk=self.pk).select_related('related_person')

                child = self.person
                parent = self.related_person
                if child.birth_date and parent.birth_date and parent.birth_date >= child.birth_date:
                    raise ValidationError(
                        f"Ota/ona ({parent.full_name}) farzandidan ({child.full_name}) oldin tug‘ilgan bo‘lishi shart!"
                    )

                parent_gender = parent.gender
                for rel in existing_parents:
                    if rel.related_person.gender == parent_gender:
                        gender_name = "otasi" if parent_gender == DeceasedPerson.GENDER_MALE else "onasi"
                        raise ValidationError(
                            f"Ushbu marhumning tizimda allaqachon {gender_name} ({rel.related_person.full_name}) mavjud!"
                        )

            # Turmush o'rtoqlik ikki tomonlama: B<->A yozuvi bo'lsa, A<->B takrorlanmasligi kerak
            elif self.relationship_type == RelationshipType.SPOUSE:
                reverse_exists = FamilyRelationship.objects.filter(
                    person_id=self.related_person_id,
                    related_person_id=self.person_id,
                    relationship_type=RelationshipType.SPOUSE,
                ).exclude(pk=self.pk).exists()
                if reverse_exists:
                    raise ValidationError("Ushbu turmush o‘rtoqlik aloqasi allaqachon kiritilgan!")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.relationship_type == RelationshipType.PARENT:
            return f"{self.related_person.full_name} -> {self.person.full_name} (Ota/Ona)"
        return f"{self.person.full_name} <-> {self.related_person.full_name} (Turmush o‘rtog‘i)"


def generate_unique_public_token() -> str:
    """Xavfsiz, taxmin qilish imkonsiz 16-baytli URL-safe token yaratish."""
    while True:
        token = secrets.token_urlsafe(16)
        if not QRCodeRecord.objects.filter(public_token=token).exists():
            return token


class QRCodeRecord(models.Model):
    """Marhumning doimiy va o'zgarmas QR-kod token yozuvi.
    
    Qabr toshiga tushiriladigan QR-kod URL shu token asosida shakllanadi:
    https://DOMAIN.UZ/m/{public_token}
    
    QR-kod toshga bir marta uriladi, shajara va marhum ma'lumotlari
    esa yillar davomida serverda xohlagancha yangilanaveradi.
    """
    deceased_person = models.OneToOneField(
        DeceasedPerson,
        on_delete=models.CASCADE,
        related_name='qr_record',
        verbose_name="Tegishli marhum"
    )
    public_token = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        editable=False,
        verbose_name="Doimiy ommaviy token"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Faol"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Yaratilgan vaqti"
    )

    class Meta:
        verbose_name = "QR-kod Yozuvi"
        verbose_name_plural = "QR-kod Yozuvlari"

    def save(self, *args, **kwargs):
        if not self.public_token:
            self.public_token = generate_unique_public_token()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"QR: {self.deceased_person.full_name} [{self.public_token}]"


class AuditLog(models.Model):
    """Tizim ichidagi xavfsizlik va o'zgarishlarni qayd etuvchi ichki audit jurnali."""
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Foydalanuvchi"
    )
    action = models.CharField(
        max_length=100,
        verbose_name="Amal turi"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP manzili"
    )
    details = models.JSONField(
        default=dict,
        verbose_name="Tafsilotlar"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Vaqt tamg‘asi"
    )

    class Meta:
        verbose_name = "Audit Jurnali"
        verbose_name_plural = "Audit Jurnallari"
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M:%S}] {self.action} by {self.user}"
