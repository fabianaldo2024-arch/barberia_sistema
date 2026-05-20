from django.contrib import admin
from .models import Barbero, Turno

@admin.register(Barbero)
class BarberoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especialidad')
    search_fields = ('nombre',)

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('cliente_nombre', 'barbero', 'fecha_hora', 'estado')
    list_filter = ('estado', 'barbero', 'fecha_hora')
