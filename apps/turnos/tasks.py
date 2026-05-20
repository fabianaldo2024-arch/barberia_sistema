from celery import shared_task
from django.utils import timezone
from .models import Turno
# Aquí importarías tu cliente de mensajería (Twilio o WhatsApp Business API) [4]

@shared_task
def enviar_recordatorio_turno(turno_id):
    """
    Tarea de Celery que envía el mensaje al cliente.
    """
    try:
        turno = Turno.objects.get(id=turno_id)
        
        # Construcción del mensaje según especificación [3]
        mensaje = (
            f"Recordatorio de tu turno:\n"
            f"Fecha y Hora: {turno.fecha_hora}\n"
            f"Barbero: {turno.barbero.nombre}\n"
            f"Dirección: Calle Falsa 123, Barbería Central"
        )
        
        # Lógica para enviar el mensaje vía SMS o WhatsApp [3], [4]
        print(f"Enviando recordatorio a {turno.cliente_celular}: {mensaje}")
        # cliente.messages.create(body=mensaje, to=turno.cliente_celular, ...)
        
    except Turno.DoesNotExist:
        pass