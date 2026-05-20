from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from .forms import TurnoForm
from apps.turnos.tasks import enviar_recordatorio_turno

def solicitar_turno(request):
    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            # 1. Guardamos el turno una sola vez [4]
            turno = form.save()

            # 2. Calculamos el recordatorio 2 horas antes [2, 3]
            ejecucion_eta = turno.fecha_hora - timedelta(hours=2)
            
            # 3. Programamos la tarea asíncrona en Celery [3]
            enviar_recordatorio_turno.apply_async((turno.id,), eta=ejecucion_eta)

            # 4. Lógica de notificación a la recepcionista [1]
            asunto = f"Nuevo turno: {turno.cliente_nombre}"
            mensaje = (
                f"Se ha registrado un nuevo turno.\n\n"
                f"Cliente: {turno.cliente_nombre}\n"
                f"Celular: {turno.cliente_celular}\n"
                f"Barbero: {turno.barbero}\n"
                f"Fecha y Hora: {turno.fecha_hora}"
            )
            
            try:
                send_mail(
                    asunto,
                    mensaje,
                    settings.EMAIL_HOST_USER,
                    ['correo-recepcionista@gmail.com'], # Configurado según [1]
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error enviando correo: {e}")

            # 5. Redirigimos a la página de éxito [5]
            return render(request, 'turnos/exito.html')
    else:
        form = TurnoForm()

    return render(request, 'turnos/solicitar_turno.html', {'form': form})