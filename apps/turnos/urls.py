from django.urls import path
from . import views

urlpatterns = [
    # Ruta para el formulario público de solicitud de turnos
    path('solicitar/', views.solicitar_turno, name='solicitar_turno'),
]