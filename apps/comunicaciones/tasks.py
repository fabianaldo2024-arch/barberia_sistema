"""
tasks.py — Acá conectamos con Celery, que ya estaba configurado en
settings.py pero sin ninguna tarea escrita.

HONESTIDAD IMPORTANTE SOBRE WHATSAPP/SMS:
El email SÍ lo podemos mandar gratis, porque ya tenés EMAIL_BACKEND SMTP
configurado (Gmail). WhatsApp y SMS son distintos: no existe una forma
gratuita de mandarlos de forma automática y confiable. Requieren contratar
un servicio externo de pago —el más usado es Twilio, también existe la
API oficial de WhatsApp Business—, que cobra por mensaje enviado.

Dejo las funciones de WhatsApp/SMS armadas con la MISMA estructura que el
email, así el día que decidas contratar Twilio (o el que sea), solo hay
que completar el cuerpo de la función con las 4-5 líneas de su SDK. La
tarea periódica y la lógica de "a quién avisar" no cambian nada.
"""

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

from apps.turnos.models import Turno
from .models import Notificacion


@shared_task
def enviar_recordatorio_email(turno_id: int):
    """
    Manda el recordatorio por email de UN turno puntual.
    Se llama desde la tarea periódica de abajo, o se puede llamar a mano
    para reenviar un recordatorio puntual.
    """
    # Cortamos temprano si ya se mandó, para no duplicar en un reintento.
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
    """
    NO IMPLEMENTADO todavía — placeholder para cuando se contrate un
    proveedor (ej. Twilio). La lógica de "no duplicar" y "buscar el turno"
    queda igual que en el email; solo cambiaría el bloque de envío real.
    """
    raise NotImplementedError(
        "Requiere integrar un proveedor externo de WhatsApp (ej. Twilio). "
        "No hay forma gratuita de enviar WhatsApp automatizado."
    )


@shared_task
def enviar_recordatorio_sms(turno_id: int):
    """NO IMPLEMENTADO — mismo caso que WhatsApp, requiere proveedor de pago."""
    raise NotImplementedError(
        "Requiere integrar un proveedor externo de SMS (ej. Twilio)."
    )


@shared_task
def revisar_turnos_de_manana():
    """
    TAREA PERIÓDICA. No la programamos con CELERY_BEAT_SCHEDULE en
    settings.py — usamos django_celery_beat (ya está instalado en
    INSTALLED_APPS) que guarda la periodicidad en la base de datos y se
    configura desde el admin de Django, en "Periodic tasks". Ahí creás
    una entrada que apunte a 'apps.comunicaciones.tasks.revisar_turnos_de_manana'
    con un Crontab Schedule de, por ejemplo, todos los días a las 18:00.

    Esta función busca los turnos de mañana y dispara un recordatorio de
    email por cada uno. delay() encola la tarea para que la ejecute un
    worker de Celery en paralelo, en vez de mandar los emails uno por uno
    de forma bloqueante acá mismo.
    """
    manana = timezone.localdate() + timedelta(days=1)
    turnos_de_manana = Turno.objects.filter(
        fecha_hora__date=manana,
        estado__in=['pendiente', 'confirmado'],
    )

    for turno in turnos_de_manana:
        enviar_recordatorio_email.delay(turno.id)

    return f"procesados: {turnos_de_manana.count()}"
