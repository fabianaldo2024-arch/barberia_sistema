from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Conectamos las URLs de la aplicación de turnos
    path('turnos/', include('apps.turnos.urls')),
]
