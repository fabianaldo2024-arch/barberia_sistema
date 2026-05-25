from django.urls import path
from . import views

urlpatterns = [
    # Mantiene la ruta larga que ya funciona
    path('solicitar/', views.solicitar_turno, name='solicitar_turno'),
    
    # SOLUCIÓN: Permite que /turnos/ cargue el formulario directamente
    path('', views.solicitar_turno, name='formulario_inicio'),
]