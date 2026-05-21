import os
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
from .models import Turno

@shared_task
def enviar_notificacion_recepcionista(turno_id):
    """Envía un email inmediato a la recepción cuando se crea un turno."""
    try:
        turno = Turno.objects.get(id=turno_id)
        asunto = "NUEVO TURNO REGISTRADO"
        mensaje = (
            f"Se ha registrado un nuevo turno:\n\n"
            f"👤 Cliente: {turno.cliente_nombre}\n"
            f"📞 Celular: {turno.cliente_celular}\n"
            f"💈 Barbero: {turno.barbero.nombre}\n"
            f"📅 Fecha y Hora: {turno.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
        )
        send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, ['recepcion@tubarberia.com'])
        return f"Email enviado para el turno {turno_id}"
    except Exception as e:
        return f"Error en email: {e}"

@shared_task
def enviar_recordatorio_turno(turno_id):
    """Envía el recordatorio por Twilio 2 horas antes de la cita."""
    try:
        turno = Turno.objects.get(id=turno_id)
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        client = Client(account_sid, auth_token)

        cuerpo = (
            f"Hola {turno.cliente_nombre}, recordatorio de tu turno:\n"
            f"⏰ Hora: {turno.fecha_hora.strftime('%H:%M')}\n"
            f"💈 Barbero: {turno.barbero.nombre}\n"
            f"📍 Dirección: Calle Falsa 123"
        )

        client.messages.create(
            body=cuerpo,
            from_=os.getenv('TWILIO_PHONE_NUMBER'),
            to=turno.cliente_celular
        )
        return f"Recordatorio enviado a {turno.cliente_celular}"
    except Exception as e:
        return f"Error en Twilio: {e}"