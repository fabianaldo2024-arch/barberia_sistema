from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .forms import TurnoForm
from .models import Turno
from .tasks import (
    notificar_recepcionista_nuevo_turno, 
    enviar_recordatorio_whatsapp, 
    enviar_promocion_masiva
)
from datetime import timedelta, datetime

def solicitar_turno(request):
    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            nuevo_turno = form.save()
            
            # 1. Notificación inmediata a recepción [3]
            # Pasamos los datos necesarios como un diccionario para la tarea de Celery
            datos_recepcion = {
                'cliente': nuevo_turno.cliente_nombre,
                'celular': nuevo_turno.cliente_celular,
                'barbero': nuevo_turno.barbero.nombre,
                'fecha': nuevo_turno.fecha_hora.strftime('%d/%m/%Y'),
                'hora': nuevo_turno.fecha_hora.strftime('%H:%M')
            }
            notificar_recepcionista_nuevo_turno.delay(datos_recepcion)
            
            # 2. Programar recordatorio para 2 horas antes de la cita [2, 4]
            # IMPORTANTE: Usamos 'enviar_recordatorio_whatsapp' (el nombre correcto)
            momento_recordatorio = nuevo_turno.fecha_hora - timedelta(hours=2)
            enviar_recordatorio_whatsapp.apply_async(
                args=[nuevo_turno.id],
                eta=momento_recordatorio
            )
            
            # Redirigir a la página de éxito configurada anteriormente
            return render(request, 'turnos/confirmacion.html', {'turno': nuevo_turno})
    else:
        form = TurnoForm()
    
    return render(request, 'turnos/solicitar_turno.html', {'form': form})

@staff_member_required
def panel_promociones(request):
    mensaje_estado = None
    if request.method == 'POST':
        texto_promo = request.POST.get('mensaje')
        if texto_promo:
            # Disparamos la tarea masiva respetando el consentimiento del cliente [2]
            enviar_promocion_masiva.delay(texto_promo)
            mensaje_estado = "¡La campaña ha sido enviada al servidor de mensajería!"
            
    return render(request, 'turnos/panel_promociones.html', {'mensaje_estado': mensaje_estado})

def dar_de_baja_promociones(request, celular):
    # Buscamos por el campo 'celular' y desactivamos el consentimiento [2, 5]
    Turno.objects.filter(celular=celular).update(acepta_promociones=False)
    return render(request, 'turnos/baja_exitosa.html')