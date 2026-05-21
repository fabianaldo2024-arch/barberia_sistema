from django import forms
from .models import Turno
from datetime import time

class TurnoForm(forms.ModelForm):
    # Definimos el campo fecha_hora específicamente para aceptar el formato de la imagen
    fecha_hora = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'placeholder': 'DD/MM/YYYY HH:MM',
            'type': 'text' # O 'datetime-local' para usar el calendario del navegador
        })
    )

    class Meta:
        model = Turno
        fields = ['cliente_nombre', 'cliente_celular', 'barbero', 'fecha_hora', 'acepta_promociones']
        widgets = {
            'cliente_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'cliente_celular': forms.TextInput(attrs={'class': 'form-control'}),
            'barbero': forms.Select(attrs={'class': 'form-select'}),
            'acepta_promociones': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_hora = cleaned_data.get('fecha_hora')
        barbero = cleaned_data.get('barbero')

        if fecha_hora and barbero:
            dia_semana = fecha_hora.weekday()
            hora_turno = fecha_hora.time()

            # Validación de Horario Comercial (L-V 09:00-19:00, S 09:00-14:00)
            if 0 <= dia_semana <= 4:
                if not (time(9, 0) <= hora_turno <= time(19, 0)):
                    raise forms.ValidationError("De lunes a viernes atendemos de 09:00 a 19:00.")
            elif dia_semana == 5:
                if not (time(9, 0) <= hora_turno <= time(14, 0)):
                    raise forms.ValidationError("Los sábados atendemos de 09:00 a 14:00.")
            elif dia_semana == 6:
                raise forms.ValidationError("La barbería está cerrada los domingos.")

            # Validación de Solapamiento
            if Turno.objects.filter(barbero=barbero, fecha_hora=fecha_hora).exists():
                raise forms.ValidationError(f"El barbero {barbero} ya tiene un turno a esa hora.")

        return cleaned_data