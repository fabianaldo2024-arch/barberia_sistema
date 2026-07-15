"""
models.py — El registro administrativo de licencias.

POR QUÉ ESTO EXISTE ADEMÁS DE LA FIRMA CRIPTOGRÁFICA:
La firma (crypto.py) te dice "este código lo generé yo y no fue alterado".
Pero no te permite REVOCAR una licencia ya emitida. Si el cliente de tu
plan Premium deja de pagar a mitad de camino, la firma va a seguir siendo
"válida" hasta la fecha de expiración original — vos no podés cambiar
retroactivamente algo que ya firmaste matemáticamente.

Por eso necesitás este modelo: es la fuente de verdad que SÍ podés
modificar en cualquier momento (activa=False) para cortar el acceso,
independientemente de lo que diga la firma. La validación completa de
una licencia siempre exige las DOS cosas: firma matemáticamente válida
Y registro marcado como activo en esta tabla.
"""

from django.db import models
from django.utils import timezone


class Licencia(models.Model):
    PLAN_CHOICES = [
        ("basico", "Básico"),
        ("pro", "Pro"),
        ("premium", "Premium"),
    ]

    codigo = models.TextField(
        unique=True,
        help_text="El código firmado completo (payload.firma) entregado al cliente.",
    )
    licencia_id = models.UUIDField(
        help_text="Extraído del payload al generar el código; permite buscarlo sin decodificar todo.",
    )
    cliente = models.CharField(max_length=200)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)

    fecha_emision = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(
        help_text="Debe coincidir con el 'exp' firmado dentro del código; se guarda también acá para poder filtrar/reportar en el admin sin decodificar.",
    )

    activa = models.BooleanField(
        default=True,
        help_text="Apagalo para revocar el acceso al instante, aunque la firma y la fecha sigan siendo válidas.",
    )

    # Fingerprint opcional: atar la licencia a una instalación puntual
    # (dominio, IP, o un hash generado en el primer uso) para que copiar
    # la carpeta entera a otro servidor no alcance para seguir usando el código.
    fingerprint_instalacion = models.CharField(
        max_length=128, blank=True, default="",
        help_text="Se completa automáticamente la primera vez que la licencia se activa con éxito.",
    )

    notas = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Licencia"
        verbose_name_plural = "Licencias"
        ordering = ["-fecha_emision"]

    def __str__(self):
        estado = "activa" if self.esta_vigente() else "inactiva/vencida"
        return f"{self.cliente} — {self.get_plan_display()} ({estado})"

    def esta_vigente(self) -> bool:
        return self.activa and self.fecha_expiracion > timezone.now()

    def dias_restantes(self) -> int:
        delta = self.fecha_expiracion - timezone.now()
        return max(delta.days, 0)
