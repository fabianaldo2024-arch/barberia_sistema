from django.contrib import admin

from django.utils.html import format_html
from django.templatetags.static import static

from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Turno

# Definimos qué datos se van a exportar (Recurso)
class TurnoResource(resources.ModelResource):
    class Meta:
        model = Turno
        # Solo exportamos los campos útiles para marketing
        fields = ('cliente_nombre', 'cliente_celular', 'acepta_promociones')
        export_order = ('cliente_nombre', 'cliente_celular', 'acepta_promociones')

# Configuramos el panel de administración con capacidad de exportación
@admin.register(Turno)
class TurnoAdmin(ImportExportModelAdmin): # Cambiamos admin.ModelAdmin por este
    resource_class = TurnoResource # Conectamos el recurso de exportación
    
    # Configuración visual que ya tenías
    list_display = ('fecha_hora', 'cliente_nombre', 'cliente_celular', 'barbero', 'acepta_promociones')
    list_filter = ('barbero', 'fecha_hora', 'acepta_promociones')
    search_fields = ('cliente_nombre', 'cliente_celular')
    ordering = ('fecha_hora',)

# NUEVO

# Personalización del encabezado del Admin
admin.site.site_header = format_html(
    '<img src="{}" style="height: 40px; margin-right: 10px;"> Gestión de Barbería',
    static('img/logo_barberia.png')
)
admin.site.site_title = "Barbería Sistema Admin"
admin.site.index_title = "Panel de Control de Turnos"