import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Cargar variables de entorno
load_dotenv()

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Seguridad
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# -------------------------------------------------------------------
# APLICACIONES (unificadas, sin duplicados)
# -------------------------------------------------------------------
INSTALLED_APPS = [
    # Django básico
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Terceros
    'import_export',          # Exportar a Excel/CSV
    'django_celery_beat',     # Periodicidad de recordatorios

    # Tus apps
    'apps.turnos',
    'apps.comunicaciones',
]

# -------------------------------------------------------------------
# MIDDLEWARE (orden correcto, sin duplicados)
# -------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # Para archivos estáticos en producción
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',    # ← NUEVO: necesario para i18n
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],   # Ruta global de plantillas
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# -------------------------------------------------------------------
# BASE DE DATOS
# -------------------------------------------------------------------
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
    )
}

# -------------------------------------------------------------------
# VALIDACIÓN DE CONTRASEÑAS
# -------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------------------------------------------------
# INTERNACIONALIZACIÓN (i18n) - ¡NUEVO!
# -------------------------------------------------------------------
LANGUAGE_CODE = 'es-ar'                # Idioma por defecto
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_L10N = True                        # Para formatos regionales
USE_TZ = True

# Idiomas soportados (español y portugués)
LANGUAGES = [
    ('es', 'Español'),
    ('pt-br', 'Português (Brasil)'),               # Puedes cambiar a 'pt-br' si prefieres
]

# Ruta donde se guardarán los archivos de traducción (.po y .mo)
LOCALE_PATHS = [
    BASE_DIR / 'locale',               # Crea esta carpeta en la raíz del proyecto
]

# -------------------------------------------------------------------
# ARCHIVOS ESTÁTICOS
# -------------------------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# -------------------------------------------------------------------
# CAMPO POR DEFECTO
# -------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------------------------------------------------------
# CONFIGURACIÓN DE EMAIL (SMTP)
# -------------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'doalperez12@gmail.com'
EMAIL_HOST_PASSWORD = 'tu-contraseña-de-aplicacion'   # ¡Cambia esto!
DEFAULT_FROM_EMAIL = 'Barbería Sistema <dolperez12@gmail.com>'

# -------------------------------------------------------------------
# CELERY
# -------------------------------------------------------------------
CELERY_TIMEZONE = TIME_ZONE

# En producción, Render va a proveer REDIS_URL automáticamente
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
