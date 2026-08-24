from django.urls import path
from . import views

urlpatterns = [
    path('solicitar/', views.solicitar_turno, name='solicitar_turno'),
    path('promociones/', views.panel_promociones, name='panel_promociones'),
    path('baja/<str:celular>/', views.dar_de_baja_promociones, name='dar_de_baja_promociones'),
    path('recibo/<int:pago_id>/', views.generar_recibo, name='generar_recibo'),  # <-- NUEVA
]