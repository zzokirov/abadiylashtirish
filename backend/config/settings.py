"""Django settings for Abadiy Xotira project.

Generated for production-grade deployment with security, caching,
and custom family tree / cemetery management logic.
"""

import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file if available
load_dotenv(BASE_DIR.parent / '.env')
load_dotenv(BASE_DIR / '.env')



def env_bool(name: str, default: bool) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in ('true', '1', 't', 'yes')


def env_list(name: str, default: str) -> list:
    return [item.strip() for item in os.environ.get(name, default).split(',') if item.strip()]


DEBUG = env_bool('DJANGO_DEBUG', True)

_DEV_SECRET_KEY = 'django-insecure-abadiy-xotira-system-dev-key-change-in-production-!@#$'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', _DEV_SECRET_KEY)
if not DEBUG and (SECRET_KEY == _DEV_SECRET_KEY or 'change-this' in SECRET_KEY):
    raise ImproperlyConfigured(
        "Production rejimida (DJANGO_DEBUG=False) DJANGO_SECRET_KEY ni albatta o'zgartiring."
    )

ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0')

# Public Memorial Base URL for QR codes: e.g. https://domain.uz/m/{token}
# Ommaviy sahifa Django tomonidan /m/<token>/ manzilida beriladi.
FRONTEND_PUBLIC_BASE_URL = os.environ.get(
    'FRONTEND_PUBLIC_BASE_URL',
    'http://localhost:8000/m'
).rstrip('/')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party packages
    'rest_framework',
    'corsheaders',

    # Local apps
    'apps.core.apps.CoreConfig',
    'apps.qr.apps.QrConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database configuration
# Uses PostgreSQL if DB_NAME is set, otherwise falls back to SQLite for easy local test/dev
DB_ENGINE = os.environ.get('DB_ENGINE', 'django.db.backends.postgresql')
DB_NAME = os.environ.get('DB_NAME')

if DB_NAME:
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': DB_NAME,
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'CONN_MAX_AGE': 60,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 10},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (Photos, QR code images)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '120/minute',
        'user': '1000/minute',
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = env_list('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000')
CORS_ALLOW_CREDENTIALS = True

# Django 4+ da HTTPS domen orqali admin formalarini yuborish uchun zarur
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS', 'http://localhost,http://127.0.0.1,http://localhost:3000')

CORS_ALLOW_METHODS = [
    'GET',
    'OPTIONS',
    'HEAD',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
]

# Rasm yuklash chegarasi (nginx client_max_body_size bilan mos)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# Security Headers
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Nginx proksi ortida HTTPS ni to'g'ri aniqlash
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Sayt HTTPS orqali ishlaganda yoqiladi. Oddiy http://localhost da yoqilsa,
# brauzer xavfsiz cookie'larni yubormaydi va admin paneliga kirib bo'lmaydi.
USE_HTTPS = env_bool('DJANGO_USE_HTTPS', False)
if USE_HTTPS:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'INFO' if not DEBUG else 'WARNING'},
}
