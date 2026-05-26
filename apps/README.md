--------------------------------------------------------------------------------
# Sistema de Gestión de Turnos - Barbería 💈

Este es un sistema integral desarrollado en **Python** que permite automatizar la reserva de citas, la gestión administrativa y la comunicación con los clientes [1].

## 📋 Descripción General
La aplicación ofrece un flujo completo desde que el cliente solicita su turno hasta que se le envía un recordatorio automático [1, 4]. Está diseñada para ser escalable y segura, utilizando procesamiento asíncrono para no interferir con la experiencia del usuario [2, 5].

## ✨ Funcionalidades Principales
*   **Reserva Online:** Formulario público donde el cliente ingresa su nombre, celular y elige su barbero favorito según la disponibilidad horaria [1, 6].
*   **Panel de Administración (Django Admin):** Gestión centralizada de turnos, barberos y usuarios con acceso protegido [7-9].
*   **Notificaciones Inteligentes:**
    *   **Envío de Correo:** Notificación inmediata a la recepción con los datos del nuevo turno [7].
    *   **Recordatorios de WhatsApp/SMS:** Programación dinámica para avisar al cliente exactamente **2 horas antes** de su cita [4, 10].
*   **Gestión de Promociones:** Panel para enviar mensajes masivos a clientes que otorgaron su consentimiento para recibir novedades [4, 9].
*   **Mantenimiento Automático:** Tarea periódica configurada para limpiar registros de turnos antiguos de la base de datos [8].

## 🛠️ Stack Tecnológico
*   **Framework Principal:** Django (Backend y Panel de Control) [2, 11].
*   **Gestión de Tareas:** Celery + Redis (Message Broker y Backend de Resultados) [2, 5].
*   **Scheduler:** Celery Beat para la periodicidad dinámica de recordatorios [5].
*   **Comunicaciones:** Twilio SDK (WhatsApp/SMS) y SMTP para correos electrónicos [12].
*   **Interfaz:** Bootstrap + Jinja2 (Templates responsivos) [13].
*   **Archivos Estáticos:** WhiteNoise [14].
*   **Seguridad:** Python-dotenv para el manejo de variables de entorno (.env) [3].

## ⚙️ Instalación y Configuración

1. **Instalar dependencias:**
   ```bash
   poetry install
Configurar el entorno: Crea un archivo .env y añade tus credenciales (SECRET_KEY, DB_URL, TWILIO_AUTH, etc.)
.
Preparar la base de datos:
Crear usuario administrador:
🚀 Ejecución del Sistema
Para el funcionamiento completo, debes correr estos tres procesos en terminales separadas:
Servidor Web: poetry run python manage.py runserver
Worker de Celery: poetry run celery -A core worker -l info
Celery Beat: poetry run celery -A core beat -l info