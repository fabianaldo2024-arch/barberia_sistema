from django.contrib import admin
from .models import Barbero, Turno, Servicio, Cliente, Pago


@admin.register(Barbero)
class BarberoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "especialidad", "porcentaje_comision")


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio", "duracion_minutos", "activo")
    list_filter = ("activo",)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "celular", "email", "acepta_promociones", "total_visitas")
    search_fields = ("nombre", "celular")

    def total_visitas(self, obj):
        return obj.total_visitas()


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ("cliente_nombre", "barbero", "servicio", "fecha_hora", "estado")
    list_filter = ("estado", "barbero")


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("turno", "monto", "metodo_pago", "fecha_pago", "comision_barbero")
    list_filter = ("metodo_pago",)
