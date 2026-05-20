from django import forms
from .models import Turno

class TurnoForm(forms.ModelForm):
    """
    Formulario para que los clientes soliciten turnos.
    Cumple con el requisito de capturar nombre, celular y barbero.
    """
    class Meta:
        model = Turno
        fields = ['cliente_nombre', 'cliente_celular', 'barbero', 'fecha_hora']
        
        # Personalizamos las etiquetas para que sean claras para el cliente
        labels = {
            'cliente_nombre': 'Nombre Completo',
            'cliente_celular': 'Celular (con código de área)',
            'barbero': 'Selecciona tu Barbero',
            'fecha_hora': 'Fecha y Hora del Turno',
        }
        
        # Añadimos estilos y tipos de entrada específicos
        widgets = {
            'cliente_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan Pérez'}),
            'cliente_celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +54911...'}),
            'fecha_hora': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'barbero': forms.Select(attrs={'class': 'form-select'}),
            }