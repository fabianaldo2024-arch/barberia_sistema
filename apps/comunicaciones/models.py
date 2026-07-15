from django.db import models


class Notificacion(models.Model):
    """
    Registra cada notificación enviada. Sin esto, si la tarea de Celery se
    ejecuta dos veces por algún reintento o solapamiento, el cliente podría
    recibir el mismo recordatorio duplicado. Antes de enviar, la tarea
    consulta si ya existe un registro para ese turno+canal.
    """
    CANALES = [
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
    ]

    turno = models.ForeignKey('turnos.Turno', on_delete=models.CASCADE)
    canal = models.CharField(max_length=20, choices=CANALES)
    enviado_el = models.DateTimeField(auto_now_add=True)
    exitoso = models.BooleanField(default=True)
    detalle_error = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ('turno', 'canal')

    def __str__(self):
        return f"{self.canal} - turno #{self.turno_id} - {'OK' if self.exitoso else 'ERROR'}"
