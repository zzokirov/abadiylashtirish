#!/bin/sh
set -e

echo "=== Abadiy Xotira Backend Init ==="

# Migratsiyalarni amalga oshirish
echo "Migratsiyalar qo'llanilmoqda..."
# Diqqat: migratsiyalar repozitoriyada saqlanadi, production'da makemigrations ishlatilmaydi
python manage.py migrate --noinput

# Statik fayllarni yig'ish
echo "Statik fayllar yig'ilmoqda..."
python manage.py collectstatic --noinput

echo "Gunicorn server ishga tushirilmoqda..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-3} \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
