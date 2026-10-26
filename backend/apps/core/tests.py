"""Automated tests for DAG cycle prevention, date constraints, and API security.

Executes thorough validations on:
- Self-relationship prohibition
- Direct & deep ancestry cycle detection (DAG)
- Date range rules (birth <= death, death <= today)
- Biological constraints (single father / single mother)
- Public API Cache-Control headers and data leak prevention
"""

import datetime
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import AuditLog, Cemetery, DeceasedPerson, FamilyRelationship, RelationshipType
from .services import validate_no_ancestry_cycle, FamilyTreeService


class DeceasedValidationTestCase(TestCase):
    def setUp(self):
        self.cemetery = Cemetery.objects.create(
            name="Chig'atoy Qabristoni",
            address="Toshkent sh., Olmazor tumani"
        )

    def test_death_date_required_and_cannot_be_future(self):
        """Vafot sanasi majburiy va kelajakdagi sana bo'lishi mumkin emas."""
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        person = DeceasedPerson(
            first_name="Anvar",
            last_name="Alimov",
            death_date=tomorrow,
            cemetery=self.cemetery
        )
        with self.assertRaises(ValidationError) as ctx:
            person.clean()
        self.assertIn('death_date', ctx.exception.message_dict)

    def test_birth_date_cannot_be_after_death_date(self):
        """Tug'ilgan sana vafot sanasidan keyin bo'lishi mumkin emas."""
        person = DeceasedPerson(
            first_name="Sobir",
            last_name="Karimov",
            birth_date=datetime.date(2000, 1, 1),
            death_date=datetime.date(1990, 5, 10),
            cemetery=self.cemetery
        )
        with self.assertRaises(ValidationError) as ctx:
            person.clean()
        self.assertIn('birth_date', ctx.exception.message_dict)

    def test_qr_record_created_automatically(self):
        """Har bir marhum saqlanganda avtomatik unikal QRCodeRecord shakllanadi."""
        person = DeceasedPerson.objects.create(
            first_name="Rustam",
            last_name="Usmonov",
            death_date=datetime.date(2020, 1, 1),
            cemetery=self.cemetery
        )
        self.assertTrue(hasattr(person, 'qr_record'))
        self.assertIsNotNone(person.qr_record.public_token)
        self.assertTrue(len(person.qr_record.public_token) >= 16)


class FamilyTreeGraphDAGTestCase(TestCase):
    def setUp(self):
        self.cemetery = Cemetery.objects.create(name="Minor Qabristoni", address="Toshkent")

        # 4 avlod: Bobo -> Ota -> Bola -> Nabira
        self.bobo = DeceasedPerson.objects.create(
            first_name="Bobo",
            last_name="Qodirov",
            gender=DeceasedPerson.GENDER_MALE,
            birth_date=datetime.date(1920, 1, 1),
            death_date=datetime.date(1995, 1, 1),
            cemetery=self.cemetery
        )
        self.ota = DeceasedPerson.objects.create(
            first_name="Ota",
            last_name="Qodirov",
            gender=DeceasedPerson.GENDER_MALE,
            birth_date=datetime.date(1950, 1, 1),
            death_date=datetime.date(2015, 1, 1),
            cemetery=self.cemetery
        )
        self.bola = DeceasedPerson.objects.create(
            first_name="Bola",
            last_name="Qodirov",
            gender=DeceasedPerson.GENDER_MALE,
            birth_date=datetime.date(1975, 1, 1),
            death_date=datetime.date(2022, 1, 1),
            cemetery=self.cemetery
        )
        self.nabira = DeceasedPerson.objects.create(
            first_name="Nabira",
            last_name="Qodirov",
            gender=DeceasedPerson.GENDER_MALE,
            birth_date=datetime.date(2000, 1, 1),
            death_date=datetime.date(2023, 1, 1),
            cemetery=self.cemetery
        )

        # Bobo -> Ota
        FamilyRelationship.objects.create(
            person=self.ota,
            related_person=self.bobo,
            relationship_type=RelationshipType.PARENT
        )
        # Ota -> Bola
        FamilyRelationship.objects.create(
            person=self.bola,
            related_person=self.ota,
            relationship_type=RelationshipType.PARENT
        )
        # Bola -> Nabira
        FamilyRelationship.objects.create(
            person=self.nabira,
            related_person=self.bola,
            relationship_type=RelationshipType.PARENT
        )

    def test_prevent_self_relationship(self):
        """O'ziga o'zi qarindosh bo'lish taqiqlanadi."""
        rel = FamilyRelationship(
            person=self.bola,
            related_person=self.bola,
            relationship_type=RelationshipType.PARENT
        )
        with self.assertRaises(ValidationError):
            rel.clean()

    def test_prevent_direct_cycle(self):
        """Otaning bolasini otaga ota qilib biriktirish (to'g'ridan-to'g'ri sikl) rad etilishi kerak."""
        # Bola ning otasi Ota. Endi Otaning otasini Bola qilmoqchimiz.
        with self.assertRaises(ValidationError):
            validate_no_ancestry_cycle(child_id=self.ota.id, parent_id=self.bola.id)

    def test_prevent_deep_ancestry_cycle(self):
        """Katta bobo o'z nabirasining farzandi bo'lib qolishi (chuqur zanjir sikli) rad etilishi shart."""
        # Nabira -> Bobo ni ota qilib qo'yish mumkin emas! (Bobo nabiraga ota emas, lekin nabiraning otasi orqali ajdod)
        # Bundan ham muhimi: Bobo ning otasini Nabira qilib qo'yish (bobo ning avlodini unga ota qilish)!
        with self.assertRaises(ValidationError):
            validate_no_ancestry_cycle(child_id=self.bobo.id, parent_id=self.nabira.id)

    def test_tree_service_hierarchy_building(self):
        """FamilyTreeService markaziy shaxs atrofida to'g'ri ajdod va avlodlarni shakllantirishi."""
        tree_service = FamilyTreeService(focal_person=self.ota)
        tree = tree_service.build_full_tree()

        # Otaning ajdodlarida Bobo bo'lishi kerak
        self.assertIsNotNone(tree['paternal_ancestors'])
        self.assertEqual(tree['paternal_ancestors']['id'], self.bobo.id)

        # Otaning avlodlarida Bola bo'lishi kerak
        self.assertEqual(len(tree['descendants']), 1)
        self.assertEqual(tree['descendants'][0]['id'], self.bola.id)
        
        # Bolaning ichida Nabira bo'lishi kerak
        self.assertEqual(len(tree['descendants'][0]['children']), 1)
        self.assertEqual(tree['descendants'][0]['children'][0]['id'], self.nabira.id)


class PublicAPISecurityTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.cemetery = Cemetery.objects.create(name="Yalang'och-Ota", address="Mirzo Ulug'bek")
        self.person = DeceasedPerson.objects.create(
            first_name="Nodir",
            last_name="Hamidov",
            birth_date=datetime.date(1960, 4, 12),
            death_date=datetime.date(2021, 8, 30),
            biography="Hurmatli ustoz va muhandis.",
            cemetery=self.cemetery,
            grave_number="Sektor 4, Qabr 18",
            is_published=True,
            is_archived=False
        )
        self.token = self.person.qr_record.public_token

    def test_public_endpoint_cache_control_headers(self):
        """Ommaviy endpoint brauzerlar keshlamasligi uchun strict Cache-Control sarlavhalarini qaytarishi kerak."""
        url = reverse('public-deceased-detail', kwargs={'token': self.token})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('no-cache', response['Cache-Control'])
        self.assertIn('no-store', response['Cache-Control'])
        self.assertIn('must-revalidate', response['Cache-Control'])
        self.assertEqual(response.data['full_name'], "Hamidov Nodir")
        self.assertEqual(response.data['grave_number'], "Sektor 4, Qabr 18")

    def test_unpublished_or_archived_person_returns_404(self):
        """Ommaga yopiq yoki arxivlangan marhumning QR manzili 404 berishi kerak."""
        self.person.is_published = False
        self.person.save()

        url = reverse('public-deceased-detail', kwargs={'token': self.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_public_endpoint_does_not_leak_private_data(self):
        """Ommaviy endpoint ichki id, audit log yoki boshqaruv ma'lumotlarini oshkor qilmasligi shart."""
        url = reverse('public-deceased-detail', kwargs={'token': self.token})
        response = self.client.get(url)

        self.assertNotIn('is_published', response.data)
        self.assertNotIn('is_archived', response.data)
        self.assertNotIn('created_at', response.data)


class RelationshipRulesTestCase(TestCase):
    def setUp(self):
        self.ota = DeceasedPerson.objects.create(
            first_name="Karim", last_name="Usmonov", gender=DeceasedPerson.GENDER_MALE,
            birth_date=datetime.date(1940, 1, 1), death_date=datetime.date(2000, 1, 1),
        )
        self.ona = DeceasedPerson.objects.create(
            first_name="Zuhra", last_name="Usmonova", gender=DeceasedPerson.GENDER_FEMALE,
            birth_date=datetime.date(1945, 1, 1), death_date=datetime.date(2005, 1, 1),
        )
        self.bola = DeceasedPerson.objects.create(
            first_name="Aziz", last_name="Usmonov", gender=DeceasedPerson.GENDER_MALE,
            birth_date=datetime.date(1970, 1, 1), death_date=datetime.date(2020, 1, 1),
        )

    def test_parent_must_be_born_before_child(self):
        """Ota/ona farzandidan keyin tug'ilgan bo'lishi mumkin emas."""
        rel = FamilyRelationship(person=self.ota, related_person=self.bola, relationship_type=RelationshipType.PARENT)
        with self.assertRaises(ValidationError):
            rel.clean()

    def test_reverse_spouse_duplicate_rejected(self):
        """A<->B turmush o'rtoqligi bo'lsa, B<->A qayta kiritilmaydi."""
        FamilyRelationship.objects.create(person=self.ota, related_person=self.ona, relationship_type=RelationshipType.SPOUSE)
        with self.assertRaises(ValidationError):
            FamilyRelationship.objects.create(person=self.ona, related_person=self.ota, relationship_type=RelationshipType.SPOUSE)

    def test_tree_includes_spouse_from_both_directions(self):
        FamilyRelationship.objects.create(person=self.ota, related_person=self.ona, relationship_type=RelationshipType.SPOUSE)
        tree = FamilyTreeService(focal_person=self.ona).build_full_tree()
        self.assertEqual([s['id'] for s in tree['spouses']], [self.ota.id])


class AdminApiTestCase(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser('boss', 'boss@example.com', 'test-pass-12345')
        self.client = APIClient()
        self.client.force_authenticate(self.admin)
        self.ota = DeceasedPerson.objects.create(
            first_name="Ota", last_name="Test", gender=DeceasedPerson.GENDER_MALE,
            birth_date=datetime.date(1940, 1, 1), death_date=datetime.date(2000, 1, 1),
        )
        self.bola = DeceasedPerson.objects.create(
            first_name="Bola", last_name="Test", gender=DeceasedPerson.GENDER_MALE,
            birth_date=datetime.date(1970, 1, 1), death_date=datetime.date(2020, 1, 1),
        )
        FamilyRelationship.objects.create(person=self.bola, related_person=self.ota, relationship_type=RelationshipType.PARENT)

    def test_cycle_returns_400_not_500(self):
        """Sikl hosil qiluvchi aloqa API orqali 400 (500 emas) qaytarishi kerak."""
        response = self.client.post('/api/v1/admin/relationships/', {
            'person': self.ota.id, 'related_person': self.bola.id, 'relationship_type': 'PARENT',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_keeps_existing_dates(self):
        """PATCH faqat bitta maydonni o'zgartirganda mavjud sanalar bilan tekshiriladi."""
        response = self.client.patch(f'/api/v1/admin/deceased/{self.bola.id}/', {
            'birth_date': '2030-01-01',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('birth_date', response.data)

        response = self.client.patch(f'/api/v1/admin/deceased/{self.bola.id}/', {'grave_number': 'A-7'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(AuditLog.objects.filter(action__startswith='UPDATE_DECEASED').exists())

    def test_admin_api_requires_staff(self):
        response = APIClient().get('/api/v1/admin/deceased/')
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))


class QuickActionSecurityTestCase(TestCase):
    def test_anonymous_cannot_quick_create(self):
        """Admin bosh sahifasidagi tezkor amallar autentifikatsiyasiz ishlamasligi kerak."""
        response = self.client.post(reverse('admin-quick-create-deceased'), {
            'first_name': 'Xaker', 'last_name': 'Test', 'death_date': '2020-01-01',
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])
        self.assertFalse(DeceasedPerson.objects.filter(first_name='Xaker').exists())

    def test_staff_quick_create_reports_errors_and_succeeds(self):
        admin_user = get_user_model().objects.create_superuser('boss', 'boss@example.com', 'test-pass-12345')
        self.client.force_login(admin_user)
        future = (datetime.date.today() + datetime.timedelta(days=5)).isoformat()
        response = self.client.post(reverse('admin-quick-create-deceased'), {
            'first_name': 'Ali', 'last_name': 'Valiyev', 'death_date': future,
        }, follow=True)
        self.assertFalse(DeceasedPerson.objects.filter(first_name='Ali').exists())
        self.assertTrue(any('qo‘shilmadi' in str(m) for m in response.context['messages']))

        self.client.post(reverse('admin-quick-create-deceased'), {
            'first_name': 'Ali', 'last_name': 'Valiyev', 'death_date': '2020-01-01',
        })
        self.assertTrue(DeceasedPerson.objects.filter(first_name='Ali').exists())

    def test_admin_index_renders(self):
        admin_user = get_user_model().objects.create_superuser('boss', 'boss@example.com', 'test-pass-12345')
        self.client.force_login(admin_user)
        DeceasedPerson.objects.create(first_name="Ali", last_name="Valiyev", death_date=datetime.date(2020, 1, 1))
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Valiyev Ali")


class QRExportTestCase(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser('boss', 'boss@example.com', 'test-pass-12345')
        self.person = DeceasedPerson.objects.create(
            first_name="O‘ktam", last_name="G'ulomov <&>", death_date=datetime.date(2020, 1, 1),
        )
        self.token = self.person.qr_record.public_token

    def test_all_formats_export_for_names_with_apostrophes(self):
        self.client.force_login(self.admin)
        for fmt, content_type in (('png', 'image/png'), ('svg', 'image/svg+xml'), ('pdf', 'application/pdf')):
            url = reverse('qr:download_qr', kwargs={'token': self.token, 'export_format': fmt})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, fmt)
            self.assertEqual(response['Content-Type'], content_type)
            self.assertIn('attachment', response['Content-Disposition'])

    def test_qr_export_requires_admin(self):
        url = reverse('qr:download_qr', kwargs={'token': self.token, 'export_format': 'png'})
        self.assertIn(self.client.get(url).status_code, (401, 403))

    def test_memorial_page_renders_escaped(self):
        response = self.client.get(reverse('memorial-web-view', kwargs={'token': self.token}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('no-store', response['Cache-Control'])
        self.assertNotContains(response, "<&>")


class PhotoShapeTestCase(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser('boss', 'boss@example.com', 'test-pass-12345')
        self.client.force_login(self.admin_user)

    def _image_file(self, name='rasm.png'):
        import io
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile
        buf = io.BytesIO()
        Image.new('RGB', (40, 50), (90, 120, 100)).save(buf, format='PNG')
        return SimpleUploadedFile(name, buf.getvalue(), content_type='image/png')

    def test_quick_create_saves_photo_and_rect_shape(self):
        import shutil
        import tempfile
        media = tempfile.mkdtemp()
        try:
            with self.settings(MEDIA_ROOT=media):
                self.client.post(reverse('admin-quick-create-deceased'), {
                    'first_name': 'Rasmli', 'last_name': 'Test', 'death_date': '2020-01-01',
                    'photo_shape': 'RECT', 'photo': self._image_file(),
                })
                person = DeceasedPerson.objects.get(first_name='Rasmli')
                self.assertTrue(person.photo)
                self.assertEqual(person.photo_shape, DeceasedPerson.PHOTO_SHAPE_RECT)

                response = self.client.get(reverse('memorial-web-view', kwargs={'token': person.qr_record.public_token}))
                self.assertContains(response, 'class="portrait rect"')
        finally:
            shutil.rmtree(media, ignore_errors=True)

    def test_quick_create_rejects_non_image(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        fake = SimpleUploadedFile('virus.png', b'bu rasm emas', content_type='image/png')
        self.client.post(reverse('admin-quick-create-deceased'), {
            'first_name': 'Soxta', 'last_name': 'Test', 'death_date': '2020-01-01', 'photo': fake,
        })
        self.assertFalse(DeceasedPerson.objects.filter(first_name='Soxta').exists())

    def test_default_shape_is_circle(self):
        person = DeceasedPerson.objects.create(first_name="Ali", last_name="Valiyev", death_date=datetime.date(2020, 1, 1))
        response = self.client.get(reverse('memorial-web-view', kwargs={'token': person.qr_record.public_token}))
        self.assertContains(response, 'class="portrait"')
