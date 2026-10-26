# 🕊️ Abadiy Xotira — Elektron Shajara va Qabriston Axborot Tizimi

> **"Inson bu dunyodan o‘tsa ham, uning yaxshi amallari va nasl-nasabi abadiy yashaydi."**

Ishlab chiqarish darajasidagi (production-grade), xavfsiz va yuqori ishonchlilikka ega doimiy QR-kodli elektron shajara va qabriston boshqaruv tizimi.

---

## 📌 Asosiy Strategiya va Arxitektura Yechimi

* **O‘zgarmas (Statik) QR-kod:** Har bir marhum uchun qabr toshiga uriladigan QR-kod URL manzili doimiy (`https://domain.uz/m/{token}`). Token xavfsiz `secrets.token_urlsafe(16)` orqali shakllanadi.
* **Dinamik Shajara:** Administrator keyinchalik yangi avlodlarni (farzandlar, nabiralar) yoki ota-bobolarni kiritib borsa ham, qabr toshidagi QR-kodni almashtirish talab etilmaydi! Brauzer orqali keyingi o‘qilganda eng so‘nggi shajara yuklanadi.
* **Toshga O‘yish Standarti (Level H — 30%):** Qabr toshlari ochiq havoda (yomg‘ir, qor, quyosh, chang, mexanik yemirilish) turishini hisobga olib, barcha QR-kodlar ISO/IEC 18004 **High Error Correction (30%)** darajasida generatsiya qilinadi. Sirtining uchdan bir qismi shikastlanganda ham telefon bexato o‘qiydi.
* **DAG (Directed Acyclic Graph) Sikl Himoyasi:** Nasl-nasab mantiqida aylanma sikllar (o‘zini o‘ziga ota qilish, bobosining otasini nabirasi qilib qo‘yish) backend darajasida qat’iy taqiqlangan.
* **Kesh Nazorati:** Barcha ommaviy API va sahifalar `Cache-Control: no-cache, no-store, must-revalidate` sarlavhalari bilan ta’minlangan.

---

## 🛠️ Texnologik Stack

* **Backend:** Python 3.11+, Django 5.1, Django REST Framework (DRF)
* **Frontend:** React 18+, TypeScript, Material-UI (MUI v5), React Router v6
* **Ma’lumotlar Bazasi:** PostgreSQL 16 (indekslangan, relational integrity)
* **QR & Grafik Eksport:** `qrcode` (Pillow), `reportlab` (vektorli PDF andoza)
* **Konteynerizatsiya & Proksi:** Docker, Docker Compose, Nginx

---

## 🚀 Ishga Tushirish (Docker orqali)

### 1. Muhit parametrlarini sozlash
```bash
cp .env.example .env
```
`.env` faylidagi maxfiy kalitlar va domen nomini kiriting. `DJANGO_SECRET_KEY` majburiy — production rejimida standart kalit bilan tizim ishga tushmaydi:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```
Sayt HTTPS orqali ochilsa `DJANGO_USE_HTTPS=True` qiling (xavfsiz cookie va HSTS yoqiladi). Oddiy `http://localhost` da `False` qoldiring, aks holda admin paneliga kirib bo'lmaydi.

> ⚠️ `FRONTEND_PUBLIC_BASE_URL` — qabr toshidagi QR-kod ichidagi manzil asosi. Toshlarga QR o'yilgandan keyin uni **o'zgartirmang**.

### 2. Konteynerlarni yig'ish va ishga tushirish
```bash
docker-compose up --build -d
```

### 3. Superuser (Administrator) yaratish
```bash
docker-compose exec backend python manage.py createsuperuser
```

Tizim manzillari:
* **Foydalanuvchilar (Ommaviy QR sahifa, Django):** `http://localhost/m/{token}/`
* **Admin Paneli (Django Admin + Boshqaruv Markazi):** `http://localhost/admin/`
* **Admin Dashboard (React UI):** `http://localhost/admin-panel`
* **API Root:** `http://localhost/api/v1/`

Nginx `/m/`, `/api/`, `/admin/` so'rovlarini Django'ga yo'naltiradi, `/static/` va `/media/` fayllarini o'zi beradi, qolganini React SPA ga.

---

## 💻 Mahalliy Ishga Tushirish (Docker'siz, SQLite)
```bash
cd backend
python -m venv ../venv
../venv/Scripts/pip install -r requirements.txt
../venv/Scripts/python manage.py migrate
../venv/Scripts/python seed_data.py
../venv/Scripts/python manage.py runserver
```
`seed_data.py` admin parolini `SEED_ADMIN_PASSWORD` muhit o'zgaruvchisidan oladi, bo'lmasa tasodifiy parol yaratib ekranga chiqaradi. Mahalliy rejimda ommaviy sahifa: `http://localhost:8000/m/{token}/`.

React frontend (ixtiyoriy): `cd frontend && npm install && npm run dev` — alohida portda ishlaganda `VITE_API_URL=http://localhost:8000/api/v1` ni belgilang.

---

## 🧪 Avtomatlashtirilgan Testlarni Ishga Tushirish
Barcha mantiqiy sikllar, sanalar va kiberxavfsizlik qoidalarini tekshirish uchun:
```bash
docker-compose exec backend python manage.py test apps.core.tests
```
Yoki mahalliy muhitda:
```bash
python manage.py test apps.core.tests
```

---

## 🪦 Tosh Ustasi (Gravyura) Uchun Eksport Formatlari
Administrator paneli orqali har bir marhum uchun 3 xil professional formatda QR eksport qilinadi:
1. **PNG 300+ DPI:** Toza monoxrom yoki inversiya (qora granit uchun oq nuqtalar).
2. **SVG Vektor:** Lazer va frezer dastgohlarida o'lchamsiz masshtablash uchun.
3. **PDF Shabloni:** A4 formatidagi o'yma chizmasi, marhumning F.I.Sh., yillari va texnik eslatmalari bilan.
