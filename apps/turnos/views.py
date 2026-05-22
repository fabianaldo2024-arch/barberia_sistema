from django.shortcuts import render, redirect
from .forms import TurnoForm
from .tasks import enviar_notificacion_recepcionista, enviar_recordatorio_turno
from datetime import timedelta

def solicitar_turno(request):
    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            nuevo_turno = form.save()
            
            # 1. Notificación inmediata a recepción
            enviar_notificacion_recepcionista.delay(nuevo_turno.id)
            
            # 2. Programar recordatorio para 2 horas antes de la cita
            momento_recordatorio = nuevo_turno.fecha_hora - timedelta(hours=2)
            enviar_recordatorio_turno.apply_async(
                args=[nuevo_turno.id],
                eta=momento_recordatorio
            )
            
            return render(request, 'turnos/confirmacion.html', {'turno': nuevo_turno})
    else:
        form = TurnoForm()
    
    return render(request, 'turnos/solicitar_turno.html', {'form': form})

# NUEVO: Vista

from django.contrib.admin.views.decorators import staff_member_required
from .tasks import enviar_promocion_masiva

@staff_member_required
def panel_promociones(request):
    mensaje_estado = None
    if request.method == 'POST':
        texto_promo = request.POST.get('mensaje')
        if texto_promo:
            # Disparamos la tarea en segundo plano usando Celery
            enviar_promocion_masiva.delay(texto_promo)
            mensaje_estado = "¡La campaña ha sido enviada al servidor de mensajería!"
            
    return render(request, 'turnos/panel_promociones.html', {'mensaje_estado': mensaje_estado})

# NUEVO

def dar_de_baja_promociones(request, celular):
    # Buscamos todos los registros de ese celular y desactivamos el consentimiento
    Turno.objects.filter(cliente_celular=celular).update(acepta_promociones=False)
    return render(request, 'turnos/baja_exitosa.html')