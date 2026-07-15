"""
reportes.py — Mismo principio que comisiones.py: todo son consultas
(aggregate/annotate) sobre datos que ya existen, no tablas nuevas.
"""

from django.db.models import Sum, Count
from django.db.models.functions import TruncDate, ExtractHour, ExtractWeekDay
from .models import Pago, Turno


def facturacion_por_dia(desde, hasta):
    """
    TruncDate agrupa por día ignorando la hora exacta del pago — sin esto,
    dos pagos del mismo día a las 10:00 y a las 18:00 quedarían en grupos
    separados porque sus timestamps completos son distintos.
    """
    return (
        Pago.objects
        .filter(fecha_pago__date__gte=desde, fecha_pago__date__lte=hasta)
        .annotate(dia=TruncDate('fecha_pago'))
        .values('dia')
        .annotate(total=Sum('monto'), cantidad_pagos=Count('id'))
        .order_by('dia')
    )


def servicios_mas_pedidos(desde, hasta, top=5):
    return (
        Turno.objects
        .filter(fecha_hora__date__gte=desde, fecha_hora__date__lte=hasta, servicio__isnull=False)
        .values('servicio__nombre')
        .annotate(cantidad=Count('id'))
        .order_by('-cantidad')[:top]
    )


def horarios_pico(desde, hasta):
    """
    ExtractHour saca solo la hora (0-23) del datetime completo, para poder
    agrupar "todos los turnos de las 14hs" sin importar de qué día fueron.
    """
    return (
        Turno.objects
        .filter(fecha_hora__date__gte=desde, fecha_hora__date__lte=hasta)
        .annotate(hora=ExtractHour('fecha_hora'))
        .values('hora')
        .annotate(cantidad=Count('id'))
        .order_by('-cantidad')
    )


def dias_con_mas_demanda(desde, hasta):
    """
    ExtractWeekDay devuelve 1=domingo ... 7=sábado (convención de Django/SQL,
    ojo que no es la misma numeración que datetime.weekday() de Python puro).
    """
    return (
        Turno.objects
        .filter(fecha_hora__date__gte=desde, fecha_hora__date__lte=hasta)
        .annotate(dia_semana=ExtractWeekDay('fecha_hora'))
        .values('dia_semana')
        .annotate(cantidad=Count('id'))
        .order_by('-cantidad')
    )
