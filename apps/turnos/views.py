from django.shortcuts import render, redirect, get_object_or_404
from .models import Turno, Cliente, Pago
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .forms import TurnoForm
from .models import Turno, Cliente
from .tasks import (
    notificar_recepcionista_nuevo_turno, 
    enviar_recordatorio_whatsapp, 
    enviar_promocion_masiva
)
from datetime import timedelta, datetime


# =============================================================================
def solicitar_turno(request):
    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            nuevo_turno = form.save(commit=False)

            cliente, creado = Cliente.objects.get_or_create(
                celular=nuevo_turno.cliente_celular,
                defaults={
                    'nombre': nuevo_turno.cliente_nombre,
                    'acepta_promociones': nuevo_turno.acepta_promociones,
                },
            )
            if not creado:
                # El cliente ya existía: actualizamos datos que pudieron cambiar
                cliente.nombre = nuevo_turno.cliente_nombre
                cliente.acepta_promociones = nuevo_turno.acepta_promociones
                cliente.save()

            nuevo_turno.cliente = cliente
            nuevo_turno.save()

            # 1. Notificación inmediata a recepción
            datos_recepcion = {
                'cliente': nuevo_turno.cliente_nombre,
                'celular': nuevo_turno.cliente_celular,
                'barbero': nuevo_turno.barbero.nombre,
                'fecha': nuevo_turno.fecha_hora.strftime('%d/%m/%Y'),
                'hora': nuevo_turno.fecha_hora.strftime('%H:%M')
            }
            notificar_recepcionista_nuevo_turno.delay(datos_recepcion)

            # 2. Programar recordatorio para 2 horas antes de la cita
            momento_recordatorio = nuevo_turno.fecha_hora - timedelta(hours=2)
            enviar_recordatorio_whatsapp.apply_async(
                args=[nuevo_turno.id],
                eta=momento_recordatorio
            )

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
            enviar_promocion_masiva.delay(texto_promo)
            mensaje_estado = "¡La campaña ha sido enviada al servidor de mensajería!"

    return render(request, 'turnos/panel_promociones.html', {'mensaje_estado': mensaje_estado})


# =============================================================================
# CORREGIDO (mismo bug que enviar_promocion_masiva: filtraba sobre Turno con
# un campo 'celular' que no existe, y debía ser 'cliente_celular'). Además,
# ahora actualiza el modelo Cliente (fuente de verdad para promociones),
# no el Turno.
# =============================================================================
def dar_de_baja_promociones(request, celular):
    Cliente.objects.filter(celular=celular).update(acepta_promociones=False)
    Turno.objects.filter(cliente_celular=celular).update(acepta_promociones=False)
    return render(request, 'turnos/baja_exitosa.html')

@staff_member_required
def generar_recibo(request, pago_id):
    """
    Muestra el recibo de un pago puntual, listo para imprimir o guardar
    como PDF desde el navegador (Ctrl+P -> Guardar como PDF).

    Requiere estar logueado como staff porque el recibo puede exponer
    datos del negocio que no son para el cliente final.
    """
    pago = get_object_or_404(Pago, id=pago_id)
    return render(request, 'turnos/recibo.html', {'pago': pago})


