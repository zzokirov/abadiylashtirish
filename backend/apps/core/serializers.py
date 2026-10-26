"""Serializers for Cemetery, DeceasedPerson, and Family Tree APIs."""

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from .models import Cemetery, DeceasedPerson, FamilyRelationship


def run_model_clean(serializer: serializers.ModelSerializer, attrs: dict) -> None:
    """Model.clean() qoidalarini DRF validatsiyasida ishga tushirish.

    Tahrirlashda (PATCH/PUT) mavjud yozuv qiymatlari yangi qiymatlar bilan
    birlashtiriladi, Django ValidationError esa DRF 400 javobiga aylantiriladi
    (aks holda server 500 xatosini qaytarardi).
    """
    model = serializer.Meta.model
    if serializer.instance is not None:
        instance = model.objects.get(pk=serializer.instance.pk)
        for key, value in attrs.items():
            setattr(instance, key, value)
    else:
        instance = model(**attrs)
    try:
        instance.clean()
    except DjangoValidationError as exc:
        if hasattr(exc, 'error_dict'):
            raise serializers.ValidationError(exc.message_dict)
        raise serializers.ValidationError({'non_field_errors': exc.messages})


class CemeterySerializer(serializers.ModelSerializer):
    """Qabriston umumiy ma'lumotlari."""
    class Meta:
        model = Cemetery
        fields = ['id', 'name', 'address', 'latitude', 'longitude', 'description']


class PublicCemeterySerializer(serializers.ModelSerializer):
    """Ommaviy sahifa uchun qabriston ma'lumotlari (ichki ID siz)."""
    class Meta:
        model = Cemetery
        fields = ['name', 'address', 'latitude', 'longitude', 'description']


class PublicDeceasedDetailSerializer(serializers.ModelSerializer):
    """Doimiy QR-kod orqali ochiladigan ommaviy sahifa uchun xavfsiz serializer.
    
    Xavfsizlik talablari:
    - Admin ma'lumotlari, ichki tizim maydonlari yoki auditlar kiritilmaydi.
    - Faqat ommaga ruxsat berilgan maydonlar qaytariladi.
    """
    cemetery = PublicCemeterySerializer(read_only=True)
    public_token = serializers.CharField(source='qr_record.public_token', read_only=True)
    full_name = serializers.CharField(read_only=True)
    years = serializers.SerializerMethodField()

    class Meta:
        model = DeceasedPerson
        fields = [
            'public_token',
            'full_name',
            'first_name',
            'last_name',
            'middle_name',
            'birth_date',
            'death_date',
            'years',
            'gender',
            'photo',
            'biography',
            'cemetery',
            'grave_number',
        ]

    def get_years(self, obj) -> str:
        birth = obj.birth_date.year if obj.birth_date else '?'
        death = obj.death_date.year if obj.death_date else '?'
        return f"{birth} — {death}"


class AdminDeceasedSerializer(serializers.ModelSerializer):
    """Adminlar uchun to'liq CRUD serializer."""
    public_token = serializers.CharField(source='qr_record.public_token', read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = DeceasedPerson
        fields = [
            'id',
            'public_token',
            'full_name',
            'first_name',
            'last_name',
            'middle_name',
            'birth_date',
            'death_date',
            'gender',
            'photo',
            'biography',
            'cemetery',
            'grave_number',
            'is_published',
            'is_archived',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        run_model_clean(self, attrs)
        return attrs


class FamilyRelationshipSerializer(serializers.ModelSerializer):
    """Admin tomonidan qarindoshlik aloqalarini o'rnatish serializeri."""
    person_name = serializers.CharField(source='person.full_name', read_only=True)
    related_person_name = serializers.CharField(source='related_person.full_name', read_only=True)

    class Meta:
        model = FamilyRelationship
        fields = [
            'id',
            'person',
            'person_name',
            'related_person',
            'related_person_name',
            'relationship_type',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        # Modelning clean() metodi orqali sikl va biologik qoidalar tekshiriladi
        run_model_clean(self, attrs)
        return attrs
