from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Turno
from datetime import time


class TurnoForm(forms.ModelForm):
    fecha_hora = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'placeholder': _('DD/MM/YYYY HH:MM'),
            'type': 'text'
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

            if 0 <= dia_semana <= 4:
                if not (time(9, 0) <= hora_turno <= time(19, 0)):
                    raise forms.ValidationError(_("De lunes a viernes atendemos de 09:00 a 19:00."))
            elif dia_semana == 5:
                if not (time(9, 0) <= hora_turno <= time(14, 0)):
                    raise forms.ValidationError(_("Los sábados atendemos de 09:00 a 14:00."))
            elif dia_semana == 6:
                raise forms.ValidationError(_("La barbería está cerrada los domingos."))

            if Turno.objects.filter(barbero=barbero, fecha_hora=fecha_hora).exists():
                raise forms.ValidationError(
                    _("El barbero %(barbero)s ya tiene un turno a esa hora.") % {'barbero': barbero}
                )

        return cleaned_data
