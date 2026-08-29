# PJM Barbería — Sistema de Turnos

Sistema de gestión de turnos para barberías: reserva pública de turnos, panel
administrativo, notificaciones automáticas por email y WhatsApp, y recibos
de pago imprimibles.

## Stack tecnológico

- **Backend:** Django 5.2 (Python 3.12)
- **Gestor de dependencias:** Poetry
- **Tareas asíncronas:** Celery + Redis
- **Notificaciones:** SMTP (email) y Twilio (WhatsApp)
- **Base de datos:** SQLite (desarrollo) — compatible con PostgreSQL en producción
- **Panel admin:** Django Admin + django-admin-interface (tema personalizable)

## Funcionalidades

- Formulario público de reserva de turnos, con validación de horario de
  atención, superposición de turnos por barbero y fecha/hora pasada.
- Registro automático de clientes (evita duplicados por número de celular).
- Notificación por email a recepción ante cada turno nuevo.
- Recordatorio automático por WhatsApp 2 horas antes del turno.
- Recordatorio diario por email de los turnos del día siguiente.
- Gestión de servicios, precios y comisiones por barbero.
- Recibo de pago imprimible/PDF (comprobante interno, no es factura fiscal).
- Baja de promociones con un solo link.
- Limpieza automática de turnos pendientes sin concretar (+7 días).
- Branding personalizable por cliente (nombre, logo y colores).

## Requisitos previos

- Python 3.12+
- Poetry
- Redis (local o remoto)
- Cuenta de Gmail con "Contraseña de aplicación"
- (Opcional) Cuenta de Twilio para WhatsApp

## Instalación

```bash
git clone <url-del-repo>
cd barberia_sistema
poetry install
cp .env.example .env
```

Editá `.env` con tus valores. Mínimo necesitás: `SECRET_KEY`,
`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`.

```bash
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
```

## Cómo correr el proyecto

Se necesitan 3 procesos corriendo al mismo tiempo, cada uno en su
propia terminal:

**Terminal 1 — Redis:**
```bash
redis-server
```

**Terminal 2 — Worker de Celery:**
```bash
poetry run celery -A core worker -l info
```

**Terminal 3 — Servidor de Django:**
```bash
poetry run python manage.py runserver
```

Con las 3 arriba, entrá a http://127.0.0.1:8000/

Nota: si modificás tasks.py hay que reiniciar Celery manualmente
(Ctrl+C y volver a correr el comando). runserver se recarga solo.

## Personalización de marca
NOMBRE_NEGOCIO=Nombre del negocio
LOGO_STATIC_PATH=img/logo_del_cliente.png
COLOR_PRIMARIO=
#e63946
COLOR_ACENTO=
#1a1a1a


Subí el logo a static/img/. Para colores del admin, entrá a
/admin/admin_interface/theme/

## Estado de las notificaciones por WhatsApp

Implementado en apps/turnos/tasks.py, requiere cuenta de Twilio activa
(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER en .env).
Sin esas credenciales, el resto del sistema funciona con normalidad.

## Estructura del proyecto

core/ Configuración del proyecto
apps/turnos/ Turnos, clientes, barberos, servicios, pagos
apps/comunicaciones/ Recordatorios por email
licencias/ Sistema de licencias


## Próximos pasos

- Facturación fiscal (AFIP/ARCA).
- Activar el sistema de licencias para venta comercial.
- Panel simplificado para marcar "atendido + cobrado" en un paso.

## Licencia

Software propietario. Todos los derechos reservados.