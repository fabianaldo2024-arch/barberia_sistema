from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

from apps.turnos.models import Turno
from .models import Notificacion


@shared_task
def enviar_recordatorio_email(turno_id: int):
    if Notificacion.objects.filter(turno_id=turno_id, canal='email').exists():
        return "ya_enviado"
    try:
        turno = Turno.objects.select_related('barbero', 'cliente').get(id=turno_id)
    except Turno.DoesNotExist:
        return "turno_no_existe"
    if not turno.cliente or not turno.cliente.email:
        return "sin_email"
    try:
        send_mail(
            subject="Recordatorio de tu turno",
            message=(
                f"Hola {turno.cliente_nombre}!\n\n"
                f"Te recordamos tu turno con {turno.barbero.nombre} "
                f"el {turno.fecha_hora.strftime('%d/%m a las %H:%M')}.\n\n"
                f"¡Te esperamos!"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[turno.cliente.email],
        )
        Notificacion.objects.create(turno=turno, canal='email', exitoso=True)
        return "enviado"
    except Exception as e:
        Notificacion.objects.create(turno=turno, canal='email', exitoso=False, detalle_error=str(e))
        return f"error: {e}"


@shared_task
def enviar_recordatorio_whatsapp(turno_id: int):
    raise NotImplementedError(
        "No usar esta versión: la real está en apps/turnos/tasks.py"
    )


@shared_task
def enviar_recordatorio_sms(turno_id: int):
    raise NotImplementedError(
        "Requiere integrar un proveedor externo de SMS (ej. Twilio)."
    )


@shared_task
def revisar_turnos_de_manana():
    manana = timezone.localdate() + timedelta(days=1)
    turnos_de_manana = Turno.objects.filter(
        fecha_hora__date=manana,
        estado__in=['pendiente', 'confirmado'],
    )
    for turno in turnos_de_manana:
        enviar_recordatorio_email.delay(turno.id)
    return f"procesados: {turnos_de_manana.count()}"
