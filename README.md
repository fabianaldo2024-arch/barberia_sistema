# Barbería Sistema

Sistema de gestión para barberías desarrollado en Django: turnos, comunicaciones con clientes y administración multi-cliente por licencias.

## Características

- **Gestión de turnos**: reserva de citas, validación de horarios de atención y prevención de clientes duplicados por número de celular.
- **Comisiones de barberos**: cálculo y seguimiento de comisiones por servicio realizado.
- **Comunicaciones**: notificaciones a clientes (email vía Gmail SMTP; WhatsApp vía Twilio — ver [Pendientes](#pendientes)).
- **Tareas asíncronas y programadas**: Celery + Redis, con `django-celery-beat` para tareas periódicas y `django-celery-results` para persistir resultados.
- **Branding personalizable por cliente**: nombre del negocio, logo y colores configurables por variables de entorno, sin tocar código ni templates.
- **Internacionalización**: español y portugués (Brasil).
- **Panel de administración mejorado**: `django-admin-interface`, `django-colorfield` e importación/exportación de datos con `django-import-export`.
- **Sistema de licencias**: activación por código, pensado para distribución a múltiples clientes (módulo en desarrollo, actualmente deshabilitado en `settings.py`).

## Stack tecnológico

| Componente        | Tecnología                                |
|--------------------|--------------------------------------------|
| Backend            | Django 5.2                                 |
| Base de datos      | SQLite (desarrollo) / PostgreSQL (producción, vía `DATABASE_URL`) |
| Cola de tareas     | Celery + Redis                             |
| Servidor WSGI      | Gunicorn                                   |
| Archivos estáticos | WhiteNoise                                 |
| Notificaciones     | Gmail SMTP (email), Twilio (WhatsApp — pendiente de activar) |
| Contenedores       | Docker + Docker Compose                    |

## Requisitos

- Docker y Docker Compose (método recomendado), **o**
- Python 3.10+ y Redis instalado localmente (método manual)

## Instalación con Docker (recomendado)

Este es el método recomendado: levanta Redis, la app Django y el worker de Celery con un solo comando.

1. Cloná el repositorio y entrá a la carpeta del proyecto.
2. Copiá `.env.example` a `.env` y completá tus propias variables (nunca subas tu `.env` real al repositorio).
3. Construí las imágenes:
   ```bash
   docker-compose build
   ```
4. Levantá los servicios:
   ```bash
   docker-compose up
   ```
5. En otra terminal, aplicá las migraciones:
   ```bash
   docker-compose exec web python manage.py migrate
   ```
6. (Opcional) Creá un superusuario:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```
7. La app queda disponible en `http://localhost:8000`.

Para detener todo: `Ctrl+C`, o `docker-compose down` si lo corriste con `-d`.

## Instalación manual (sin Docker)

Requiere tener Redis corriendo localmente y tres terminales abiertas.

1. Creá y activá un entorno virtual, luego instalá dependencias:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copiá `.env.example` a `.env` y completá las variables.
3. Aplicá migraciones: `python manage.py migrate`
4. En tres terminales separadas (con el entorno virtual activado en cada una):
   ```bash
   # Terminal 1
   redis-server

   # Terminal 2
   celery -A core worker -l info

   # Terminal 3
   python manage.py runserver
   ```

## Variables de entorno

Ver `.env.example` para la lista completa. Las más relevantes:

| Variable                  | Descripción                                      |
|----------------------------|--------------------------------------------------|
| `SECRET_KEY`               | Clave secreta de Django                          |
| `DEBUG`                    | `True` en desarrollo, `False` en producción      |
| `ALLOWED_HOSTS`             | Dominios permitidos, separados por coma          |
| `DATABASE_URL`              | Si se define, usa PostgreSQL en vez de SQLite    |
| `REDIS_URL`                 | Broker/backend de Celery                         |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | Credenciales SMTP para envío de emails |
| `NOMBRE_NEGOCIO`, `LOGO_STATIC_PATH`, `COLOR_PRIMARIO`, `COLOR_ACENTO` | Branding por cliente |
| `LICENCIA_SECRET_KEY`, `LICENCIA_CODIGO_ACTIVO` | Sistema de licencias (en desarrollo) |

## Estructura del proyecto

```
barberia_sistema/
├── apps/
│   ├── turnos/            # Reserva de citas, horarios, comisiones
│   └── comunicaciones/    # Notificaciones a clientes
├── core/                  # Configuración del proyecto (settings, celery.py, urls)
├── licencias/              # Sistema de licencias (en desarrollo, no activo aún)
├── locale/                 # Traducciones (es, pt-br)
├── static/ / staticfiles/  # Archivos estáticos
├── templates/               # Plantillas HTML
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Pruebas

**Estado actual: sin cobertura de pruebas automatizadas.** El sistema maneja reglas de negocio estrictas (no duplicar clientes por celular, validación de horarios de atención, cálculo de comisiones de barberos), por lo que antes de incorporar la facturación fiscal (AFIP/ARCA) es necesario escribir pruebas automatizadas —con el sistema de pruebas nativo de Django o pytest— que cubran al menos:

- Validación de horarios de atención al crear un turno.
- Prevención de clientes duplicados por número de celular.
- Cálculo de comisiones por barbero.

Esto evita que la integración de facturación rompa el sistema de reservas existente.

## Pendientes

- [ ] Facturación fiscal electrónica (AFIP/ARCA) — aún no implementada.
- [ ] Activación de notificaciones por WhatsApp (la librería Twilio ya está en `requirements.txt`, pero la integración no está activa).
- [ ] Suite de pruebas automatizadas (ver sección [Pruebas](#pruebas)).
- [ ] Habilitar el módulo de licencias (actualmente comentado en `INSTALLED_APPS` y `MIDDLEWARE`).

## Licencia

Proyecto privado — todos los derechos reservados, salvo que se indique lo contrario.