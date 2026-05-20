import os
from celery import Celery

# Establecemos el módulo de configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# nuevo 
app = Celery('barberia_sistema')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


# Carga automáticamente las tareas de todas las aplicaciones registradas
app.autodiscover_tasks()


