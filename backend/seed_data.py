"""Initial seed script for Abadiy Xotira.

Creates:
1. Superuser "admin" (parol SEED_ADMIN_PASSWORD muhit o'zgaruvchisidan yoki tasodifiy yaratiladi)
2. Sample Cemetery ("Chig'atoy Qabristoni")
3. 3-4 generations real sample family tree:
   - Great Grandfather: Alimov O'ktam (1920 - 1985)
   - Father: Alimov Anvar O'ktamovich (1948 - 2021)
   - Mother: Karimova Malika Saidovna (1952 - 2019)
   - Child 1: Alimov Jamshid Anvarovich (1975 - 2023)
   - Child 2: Alimova Lola Anvarovna (1978 - 2022)
   - Grandchild: Alimov Sarvar Jamshidovich (2000 - 2024)
"""

import os
import secrets
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from apps.core.models import Cemetery, DeceasedPerson, FamilyRelationship, RelationshipType

User = get_user_model()

def seed():
    print("=== Abadiy Xotira Ma'lumotlarini Yaratish ===")

    # 1. Admin yaratish
    if not User.objects.filter(username='admin').exists():
        password = os.environ.get('SEED_ADMIN_PASSWORD') or secrets.token_urlsafe(12)
        User.objects.create_superuser('admin', 'admin@xotira.uz', password)
        print(f"[+] Admin superuser yaratildi: admin / {password}")
        print("    Parolni darhol eslab qoling yoki admin panelda o'zgartiring!")
    else:
        print("[*] Admin allaqachon mavjud.")

    # 2. Qabriston yaratish
    cemetery, _ = Cemetery.objects.get_or_create(
        name="Chig‘atoy Qabristoni",
        defaults={
            'address': "Toshkent shahri, Olmazor tumani, Forobiy ko‘chasi",
            'latitude': 41.341250,
            'longitude': 69.215430,
            'description': "Toshkentning eng qadimiy va ehtiromga loyiq qabristonlaridan biri."
        }
    )
    print(f"[+] Qabriston: {cemetery.name}")

    # 3. Katta Bobo
    bobo, _ = DeceasedPerson.objects.get_or_create(
        first_name="O‘ktam",
        last_name="Alimov",
        defaults={
            'middle_name': "Rahimovich",
            'gender': DeceasedPerson.GENDER_MALE,
            'birth_date': datetime.date(1920, 3, 15),
            'death_date': datetime.date(1985, 11, 20),
            'cemetery': cemetery,
            'grave_number': "Sektor 1, Qabr 12",
            'biography': "Ikkinchi jahon urushi qatnashchisi, mehnat faxriysi. Butun umrini xalq ta'limiga bag'ishlagan mo''tabar inson.",
            'is_published': True,
        }
    )

    # 4. Ota (Markaziy shaxs qilib ko'rsatish uchun)
    ota, _ = DeceasedPerson.objects.get_or_create(
        first_name="Anvar",
        last_name="Alimov",
        defaults={
            'middle_name': "O‘ktamovich",
            'gender': DeceasedPerson.GENDER_MALE,
            'birth_date': datetime.date(1948, 5, 10),
            'death_date': datetime.date(2021, 9, 14),
            'cemetery': cemetery,
            'grave_number': "Sektor 1, Qabr 14",
            'biography': "Mohir muhandis va jamoat arbobi. Toshkent shahri qurilishida ko'p yillar fidokorona mehnat qilgan. Farzandlarini ilm-fan va halollik ruhida tarbiyalagan.",
            'is_published': True,
        }
    )

    # 5. Ona (Turmush o'rtog'i)
    ona, _ = DeceasedPerson.objects.get_or_create(
        first_name="Malika",
        last_name="Karimova",
        defaults={
            'middle_name': "Saidovna",
            'gender': DeceasedPerson.GENDER_FEMALE,
            'birth_date': datetime.date(1952, 8, 22),
            'death_date': datetime.date(2019, 4, 5),
            'cemetery': cemetery,
            'grave_number': "Sektor 1, Qabr 15",
            'biography': "Mehribon ona, olijanob shifokor. Ko'plab insonlarning dardiga shifo bo'lgan, oilasining fayzi va tayanchi.",
            'is_published': True,
        }
    )

    # 6. Farzand 1
    farzand1, _ = DeceasedPerson.objects.get_or_create(
        first_name="Jamshid",
        last_name="Alimov",
        defaults={
            'middle_name': "Anvarovich",
            'gender': DeceasedPerson.GENDER_MALE,
            'birth_date': datetime.date(1975, 1, 12),
            'death_date': datetime.date(2023, 7, 3),
            'cemetery': cemetery,
            'grave_number': "Sektor 2, Qabr 45",
            'biography': "Iqtisodchi, tadbirkor. Sahovatli, do'stlarga sodiq va el-yurt xizmatida bo'lgan inson.",
            'is_published': True,
        }
    )

    # 7. Farzand 2
    farzand2, _ = DeceasedPerson.objects.get_or_create(
        first_name="Lola",
        last_name="Alimova",
        defaults={
            'middle_name': "Anvarovna",
            'gender': DeceasedPerson.GENDER_FEMALE,
            'birth_date': datetime.date(1978, 10, 30),
            'death_date': datetime.date(2022, 12, 1),
            'cemetery': cemetery,
            'grave_number': "Sektor 2, Qabr 46",
            'biography': "Filologiya fanlari nomzodi, sevimli ustoz va adabiyotshunos.",
            'is_published': True,
        }
    )

    # 8. Nabira
    nabira, _ = DeceasedPerson.objects.get_or_create(
        first_name="Sarvar",
        last_name="Alimov",
        defaults={
            'middle_name': "Jamshidovich",
            'gender': DeceasedPerson.GENDER_MALE,
            'birth_date': datetime.date(2000, 2, 18),
            'death_date': datetime.date(2024, 5, 20),
            'cemetery': cemetery,
            'grave_number': "Sektor 3, Qabr 08",
            'biography': "Dasturiy injiniring bo'yicha yosh mutaxassis. Ilmga chanqoq, xushfe'l va kamtarin yigit.",
            'is_published': True,
        }
    )

    print("[+] Marhumlar yaratildi.")

    # Qarindoshlik aloqalarini o'rnatish
    # Bobo -> Ota
    FamilyRelationship.objects.get_or_create(
        person=ota,
        related_person=bobo,
        relationship_type=RelationshipType.PARENT
    )

    # Ota <-> Ona (Turmush o'rtoqlari)
    FamilyRelationship.objects.get_or_create(
        person=ota,
        related_person=ona,
        relationship_type=RelationshipType.SPOUSE
    )

    # Ota -> Farzand 1
    FamilyRelationship.objects.get_or_create(
        person=farzand1,
        related_person=ota,
        relationship_type=RelationshipType.PARENT
    )
    # Ona -> Farzand 1
    FamilyRelationship.objects.get_or_create(
        person=farzand1,
        related_person=ona,
        relationship_type=RelationshipType.PARENT
    )

    # Ota -> Farzand 2
    FamilyRelationship.objects.get_or_create(
        person=farzand2,
        related_person=ota,
        relationship_type=RelationshipType.PARENT
    )
    # Ona -> Farzand 2
    FamilyRelationship.objects.get_or_create(
        person=farzand2,
        related_person=ona,
        relationship_type=RelationshipType.PARENT
    )

    # Farzand 1 -> Nabira
    FamilyRelationship.objects.get_or_create(
        person=nabira,
        related_person=farzand1,
        relationship_type=RelationshipType.PARENT
    )

    print("[+] Shajara aloqalari (DAG) to'liq shakllantirildi.")
    print("=" * 55)
    print(f"ASOSIY MARHUM: {ota.full_name}")
    print(f"DOIMIY QR TOKENI: {ota.qr_record.public_token}")
    print(f"OMMAVIY QR MANZILI: {settings.FRONTEND_PUBLIC_BASE_URL}/{ota.qr_record.public_token}/")
    print("=" * 55)

if __name__ == '__main__':
    seed()
