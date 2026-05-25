from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('turnos/', include('apps.turnos.urls')),
    
    # Redirección automática a la página de solicitud
    path('', RedirectView.as_view(url='/turnos/solicitar/', permanent=True)),
]
