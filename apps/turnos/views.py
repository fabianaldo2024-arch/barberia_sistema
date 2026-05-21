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