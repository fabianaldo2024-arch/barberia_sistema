"""
generar_licencia.py — Tu herramienta privada para emitir códigos.

USO (desde TU máquina, nunca en el servidor del cliente):
    python manage.py generar_licencia --cliente "Barbería El Corte" --plan pro --dias 15

Esto hace dos cosas:
  1. Crea el código firmado (crypto.generar_licencia) — matemática, offline.
  2. Lo guarda en la tabla Licencia — tu registro administrativo.

El código resultante es lo único que le mandás al cliente. La SECRET_KEY
jamás sale de tu entorno.
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import json, base64

from licencias.crypto import generar_licencia
from licencias.models import Licencia


class Command(BaseCommand):
    help = "Genera un código de licencia firmado y lo registra en la base de datos."

    def add_arguments(self, parser):
        parser.add_argument("--cliente", required=True, help="Nombre del cliente/negocio")
        parser.add_argument("--plan", required=True, choices=["basico", "pro", "premium"])
        parser.add_argument("--dias", required=True, type=int, help="Días de validez (ej: 15 para prueba, 365 para anual)")

    def handle(self, *args, **options):
        secret = getattr(settings, "LICENCIA_SECRET_KEY", None)
        if not secret:
            raise CommandError(
                "Falta LICENCIA_SECRET_KEY en settings.py / .env. "
                "Generá una con: python -c \"import secrets; print(secrets.token_hex(32))\""
            )

        codigo = generar_licencia(
            cliente=options["cliente"],
            plan=options["plan"],
            dias_validez=options["dias"],
            secret_key=secret,
        )

        # Decodificamos el payload solo para extraer el id y la fecha exacta
        # que ya quedaron firmados adentro del código, y así no calcular dos
        # veces (evita que el registro y la firma queden desincronizados).
        payload_b64 = codigo.split(".")[0]
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))

        Licencia.objects.create(
            codigo=codigo,
            licencia_id=payload["id"],
            cliente=options["cliente"],
            plan=options["plan"],
            fecha_expiracion=timezone.datetime.fromtimestamp(payload["exp"], tz=timezone.get_current_timezone()),
        )

        self.stdout.write(self.style.SUCCESS(f"\nLicencia generada para {options['cliente']} (plan {options['plan']}, {options['dias']} días)\n"))
        self.stdout.write(self.style.WARNING("Código a entregar al cliente:\n"))
        self.stdout.write(codigo + "\n")
