"""
comisiones.py — No hay ningún modelo "Comision" en la base de datos, y es
a propósito. Una comisión no es un dato que se guarda, es un CÁLCULO que
se hace sobre los pagos ya existentes. Guardarla aparte duplicaría
información (y ese duplicado se puede desincronizar del dato real si
alguien edita un Pago después). Mejor: calcular siempre en el momento,
a partir de la fuente de verdad (Pago).

Django ORM tiene herramientas para hacer esta suma directamente en SQL,
en vez de traer todos los Pagos a Python y sumarlos con un for. Eso importa
en un local con miles de pagos acumulados: sumar en la base de datos es
muchísimo más rápido que traer todo a memoria.
"""

from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from .models import Pago


def comisiones_por_barbero(desde, hasta):
    """
    Devuelve un queryset con, por cada barbero, cuánto facturó y cuánto
    le corresponde de comisión en el rango de fechas [desde, hasta].

    F('turno__barbero__porcentaje_comision') — el F() le dice al ORM
    "usá el valor de esta columna de la base de datos", no un número fijo
    de Python. Así el cálculo pasa a ser parte de la consulta SQL:
    SUM(monto * porcentaje_comision / 100), calculado por la base de datos,
    no traído campo por campo a Python.
    """
    comision_expr = ExpressionWrapper(
        F('monto') * F('turno__barbero__porcentaje_comision') / 100,
        output_field=DecimalField(max_digits=10, decimal_places=2),
    )

    return (
        Pago.objects
        .filter(fecha_pago__date__gte=desde, fecha_pago__date__lte=hasta)
        .values('turno__barbero__nombre')  # agrupa por barbero
        .annotate(
            total_facturado=Sum('monto'),
            total_comision=Sum(comision_expr),
        )
        .order_by('-total_facturado')
    )
