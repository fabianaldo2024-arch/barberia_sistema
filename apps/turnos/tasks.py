import os
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from twilio.rest import Client

from .models import Turno, Cliente


def _cliente_twilio():
    """Cliente de Twilio compartido por las tareas de WhatsApp."""
    return Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))


@shared_task
def limpiar_turnos_viejos():
    """
    Borra únicamente turnos PENDIENTES de hace más de 7 días.
    Los turnos 'atendido' NUNCA se tocan, porque borrar un Turno con Pago
    asociado se lleva el Pago en cascada y perderías historial de cobros.
    """
    limite = timezone.now() - timedelta(days=7)
    cantidad, _ = Turno.objects.filter(
        estado='pendiente',
        fecha_hora__lt=limite,
    ).delete()
    return f"Se han eliminado {cantidad} turnos pendientes sin concretar (+7 días)."


@shared_task
def notificar_recepcionista_nuevo_turno(datos_turno):
    try:
        asunto = "NUEVO TURNO REGISTRADO"
        mensaje = (
            f"Se ha registrado un nuevo turno:\n\n"
            f"👤 Cliente: {datos_turno.get('cliente', '')}\n"
            f"📞 Celular: {datos_turno.get('celular', '')}\n"
            f"💈 Barbero: {datos_turno.get('barbero', '')}\n"
            f"✂️ Servicio: {datos_turno.get('servicio', '')}\n"
            f"📅 Fecha: {datos_turno.get('fecha', '')}\n"
            f"🕒 Hora: {datos_turno.get('hora', '')}"
        )
        send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [os.getenv('EMAIL_RECEPCION', 'recepcion@tubarberia.com')])
        return f"Email enviado para el turno de {datos_turno.get('cliente', 'cliente desconocido')}"
    except Exception as e:
        return f"Error en email: {e}"


@shared_task
def enviar_promocion_masiva(texto_promo):
    try:
        client = _cliente_twilio()
        clientes_aptos = Cliente.objects.filter(acepta_promociones=True)
        contador_exitos = 0
        for cliente in clientes_aptos:
            try:
                client.messages.create(
                    body=texto_promo,
                    from_=os.getenv('TWILIO_WHATSAPP_NUMBER'),
                    to=f"whatsapp:{cliente.celular}"
                )
                contador_exitos += 1
            except Exception:
                continue
        return f"Campaña finalizada. Se enviaron {contador_exitos} mensajes."
    except Exception as e:
        return f"Error general en la campaña: {str(e)}"


@shared_task
def enviar_recordatorio_whatsapp(turno_id):
    try:
        turno = Turno.objects.select_related('barbero', 'servicio').get(id=turno_id)
    except Turno.DoesNotExist:
        return "Error: el turno ya no existe (pudo haber sido cancelado)."

    servicio_txt = turno.servicio.nombre if turno.servicio else "tu servicio"
    mensaje = (
        f"Hola {turno.cliente_nombre}! Te recordamos tu turno de {servicio_txt} "
        f"con {turno.barbero.nombre} hoy a las {turno.fecha_hora.strftime('%H:%M')}. ¡Te esperamos!"
    )
    try:
        client = _cliente_twilio()
        client.messages.create(
            body=mensaje,
            from_=os.getenv('TWILIO_WHATSAPP_NUMBER'),
            to=f"whatsapp:{turno.cliente_celular}"
        )
        return f"Recordatorio enviado a {turno.cliente_celular}"
    except Exception as e:
        return f"Error enviando recordatorio: {e}"
