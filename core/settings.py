import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Cargar variables de entorno
load_dotenv()

# ============================================================================
# DEFINICIONES BASE
# ============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-clave-temporal-no-usar-en-produccion')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',') if os.getenv('ALLOWED_HOSTS') else []

# ============================================================================
# APLICACIONES INSTALADAS
# ============================================================================
INSTALLED_APPS = [
    'admin_interface', 'colorfield',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Aplicaciones de terceros (si las usas)
    'django_celery_beat',
    'django_celery_results',
    'import_export',


    'core',
    'apps.turnos',
    'apps.comunicaciones',   # <-- AGREGAR esta línea
    # 'licencias',   # la dejamos comentada por ahora, la activamos en el paso 2 de tu plan
]



# ============================================================================
# MIDDLEWARE
# ============================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'licencias.middleware.LicenciaMiddleware',   # COMENTADO PARA DESARROLLO
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ============================================================================
# URLS Y WSGI
# ============================================================================
ROOT_URLCONF = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'

# ============================================================================
# TEMPLATES
# ============================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.contrib.messages.context_processors.messages',
                'apps.turnos.context_processors.branding',
                # 'licencias.context_processors.info_licencia',  # COMENTADO porque no existe
            ],
        },
    },
]

# ============================================================================
# BASE DE DATOS
# ============================================================================
if os.getenv('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ============================================================================
# VALIDACIÓN DE CONTRASEÑAS
# ============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================================
# INTERNACIONALIZACIÓN Y LOCALIZACIÓN
# ============================================================================
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('es', 'Español'),
    ('pt-br', 'Português (Brasil)'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# ============================================================================
# ARCHIVOS ESTÁTICOS
# ============================================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============================================================================
# CAMPO POR DEFECTO
# ============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================================
# CONFIGURACIÓN DE EMAIL (SMTP)
# ============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = f'Barbería Sistema <{EMAIL_HOST_USER}>' if EMAIL_HOST_USER else 'Barbería Sistema'

# ============================================================================
# CELERY
# ============================================================================
CELERY_TIMEZONE = TIME_ZONE
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# Variables adicionales (opcionales)
LICENCIA_SECRET_KEY = os.getenv('LICENCIA_SECRET_KEY', '')
LICENCIA_CODIGO_ACTIVO = os.getenv('LICENCIA_CODIGO_ACTIVO', '')

# ============================================================================
# BRANDING (personalizable por cliente sin tocar código ni HTML)
# ============================================================================
BRANDING = {
    'nombre_negocio': os.getenv('NOMBRE_NEGOCIO', 'PJM Barbería'),
    'logo_static_path': os.getenv('LOGO_STATIC_PATH', 'img/logo_barberia.png'),
    'color_primario': os.getenv('COLOR_PRIMARIO', '#e63946'),
    'color_acento': os.getenv('COLOR_ACENTO', '#1a1a1a'),
}