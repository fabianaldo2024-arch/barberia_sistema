import os
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
from .models import Turno

from celery import shared_task
from django.utils import timezone

@shared_task
def limpiar_turnos_viejos():
    # Borra todos los turnos cuya fecha y hora sean menores a la actual
    ahora = timezone.now()
    cantidad, _ = Turno.objects.filter(fecha_hora__lt=ahora).delete()
    return f"Se han eliminado {cantidad} turnos antiguos."


# =============================================================================
@shared_task
def notificar_recepcionista_nuevo_turno(datos_turno):
    try:
        asunto = "NUEVO TURNO REGISTRADO"
        mensaje = (
            f"Se ha registrado un nuevo turno:\n\n"
            f"👤 Cliente: {datos_turno.get('cliente', '')}\n"
            f"📞 Celular: {datos_turno.get('celular', '')}\n"
            f"💈 Barbero: {datos_turno.get('barbero', '')}\n"
            f"📅 Fecha: {datos_turno.get('fecha', '')}\n"
            f"🕒 Hora: {datos_turno.get('hora', '')}"
        )
        send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, ['recepcion@tubarberia.com'])
        return f"Email enviado para el turno de {datos_turno.get('cliente', 'cliente desconocido')}"
    except Exception as e:
        return f"Error en email: {e}"


#NUEVO
@shared_task
def enviar_promocion_masiva(texto_promo):
    try:
        # Configuración del cliente de Twilio
        client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
        
        # Filtramos únicamente los clientes que dieron su consentimiento [1]
        # El campo 'acepta_promociones' debe existir en tu modelo Turno
        clientes_aptos = Turno.objects.filter(acepta_promociones=True).values('celular').distinct()
        
        contador_exitos = 0
        for cliente in clientes_aptos:
            try:
                client.messages.create(
                    body=texto_promo,
                    from_=os.getenv('TWILIO_WHATSAPP_NUMBER'),
                    to=f"whatsapp:{cliente['celular']}"
                )
                contador_exitos += 1
            except Exception:
                continue # Si falla un número, sigue con el siguiente
                
        return f"Campaña finalizada. Se enviaron {contador_exitos} mensajes."

    except Exception as e:
        return f"Error general en la campaña: {str(e)}"


#NUEVO
@shared_task
def enviar_recordatorio_whatsapp(turno_id):
    turno = Turno.objects.get(id=turno_id)
    # Usar cliente_nombre y cliente_celular
    mensaje = f"Hola {turno.cliente_nombre}, recordamos tu turno..."
    # ... lógica de Twilio ...
    
    contador = 0
    for cliente in clientes_aptos:
        try:
            # Aquí se ejecutaría el envío real
            print(f"Enviando promo a {cliente.cliente_celular}")
            contador += 1
        except Exception as e:
            print(f"Error: {e}")
            
    return f"Campaña finalizada. {contador} mensajes procesados."