import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Cargar las variables de entorno desde el archivo .env [1]
load_dotenv()

# 2. Definir la ruta base del proyecto (BASE_DIR)
BASE_DIR = Path(__file__).resolve().parent.parent

# 3. Configuración de seguridad utilizando os.getenv() [1]
# El SECRET_KEY ya no está "hardcodeado" en el archivo
SECRET_KEY = os.getenv('SECRET_KEY')

# El modo DEBUG se activa solo si en el .env dice 'True'
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Configura los dominios permitidos (en desarrollo puedes dejarlo así)
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Debe ir aquí [2]
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... resto de middlewares ...
    'django.contrib.sessions.middleware.SessionMiddleware',
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
        'DIRS': [],
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


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es-ar' # O 'es-es' según tu país
TIME_ZONE = 'America/Argentina/Buenos_Aires' # Ajusta a tu zona horaria
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Tus aplicaciones del sistema de barbería
    'apps.turnos',
    'apps.comunicaciones',
]

# Configuración de Email SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'doalperez12@gmail.com'
EMAIL_HOST_PASSWORD = 'tu-contraseña-de-aplicacion'
DEFAULT_FROM_EMAIL = 'Barbería Sistema <dolperez12@gmail.com>'

# Configuración de Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TIMEZONE = TIME_ZONE  # Usa la misma zona horaria de tu proyecto

INSTALLED_APPS = [
    # Aplicaciones básicas y obligatorias de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Tus aplicaciones locales
    'apps.turnos',

    # Librerías externas necesarias según los requisitos técnicos
    'import_export',        # Para exportar clientes a Excel/CSV
    'django_celery_beat',   # Para la periodicidad de los recordatorios de 2 horas
]

# NUEVO HOY

import os

# Carpeta donde se buscarán los archivos estáticos durante el desarrollo
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Carpeta donde Django "juntará" todos los archivos para producción
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Habilitar la compresión y el cacheado persistente de Whitenoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
