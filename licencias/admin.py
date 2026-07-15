from django.contrib import admin
from .models import Licencia


@admin.register(Licencia)
class LicenciaAdmin(admin.ModelAdmin):
    list_display = ("cliente", "plan", "activa", "fecha_expiracion", "dias_restantes_display")
    list_filter = ("plan", "activa")
    search_fields = ("cliente", "licencia_id")
    readonly_fields = ("codigo", "licencia_id", "fecha_emision", "fingerprint_instalacion")

    def dias_restantes_display(self, obj):
        return obj.dias_restantes()
    dias_restantes_display.short_description = "Días restantes"
