from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import Turno, Servicio
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
        # AGREGADO: 'servicio'. Sin esto, todo turno se creaba con
        # servicio=None (es nullable en el modelo, así que no rompía nada,
        # pero recepción no sabía qué servicio pidió el cliente y no había
        # forma de sugerir precio/duración más adelante).
        fields = ['cliente_nombre', 'cliente_celular', 'barbero', 'servicio', 'fecha_hora', 'acepta_promociones']
        widgets = {
            'cliente_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'cliente_celular': forms.TextInput(attrs={'class': 'form-control'}),
            'barbero': forms.Select(attrs={'class': 'form-select'}),
            'servicio': forms.Select(attrs={'class': 'form-select'}),
            'acepta_promociones': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo servicios activos son elegibles al pedir un turno nuevo.
        self.fields['servicio'].queryset = Servicio.objects.filter(activo=True)
        self.fields['servicio'].required = True

    def clean(self):
        cleaned_data = super().clean()
        fecha_hora = cleaned_data.get('fecha_hora')
        barbero = cleaned_data.get('barbero')

        if fecha_hora:
            # El widget produce un datetime "naive" (sin timezone). Si el
            # proyecto usa USE_TZ=True (default de Django), lo convertimos
            # a aware acá para que se guarde y compare correctamente, y
            # para evitar el RuntimeWarning de Django en cada save().
            if timezone.is_naive(fecha_hora):
                fecha_hora = timezone.make_aware(fecha_hora, timezone.get_current_timezone())
                cleaned_data['fecha_hora'] = fecha_hora

            # NUEVO: no permitir turnos en fecha/hora ya pasada.
            if fecha_hora < timezone.now():
                raise forms.ValidationError(
                    _("No se puede pedir un turno en una fecha u hora que ya pasó.")
                )

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

            if barbero and Turno.objects.filter(barbero=barbero, fecha_hora=fecha_hora).exists():
                raise forms.ValidationError(
                    _("El barbero %(barbero)s ya tiene un turno a esa hora.") % {'barbero': barbero}
                )

        return cleaned_data