"""
crypto.py — El corazón matemático del sistema de licencias.

IDEA CENTRAL:
Un código de licencia no es un texto random que "existe o no existe" en una
tabla. Es un PAYLOAD (datos) + una FIRMA calculada con una clave secreta que
solo vos tenés. Cualquiera puede LEER el código (está en base64, no está
encriptado, es solo texto codificado), pero nadie puede FABRICAR uno nuevo
sin la clave secreta, porque la firma HMAC-SHA256 es una función de un solo
sentido: fácil de calcular hacia adelante, computacionalmente inviable de
revertir.

Por qué HMAC y no un simple hash (ej. sha256(codigo))?
Un hash simple se puede recalcular por cualquiera: hash(payload) da siempre
el mismo resultado, así que un atacante podría generar payload+hash(payload)
para cualquier dato que invente. HMAC combina el payload con una SECRET_KEY
en el cálculo, así que sin conocer esa clave es imposible reproducir la
firma, aunque el atacante vea mil ejemplos de códigos válidos.

FLUJO:
  vos (con SECRET_KEY)  →  generar_licencia()  →  código para el cliente
  cliente (sin SECRET_KEY) → validar_licencia() → True/False + datos
"""

import hmac
import hashlib
import base64
import json
import time
import uuid


class LicenciaInvalida(Exception):
    """Se lanza cuando el código no pasa la verificación de firma."""
    pass


class LicenciaExpirada(Exception):
    """La firma es válida, pero la fecha de expiración ya pasó."""
    pass


def _firmar(payload_b64: str, secret_key: str) -> str:
    """
    Calcula el HMAC-SHA256 del payload usando la clave secreta.
    Esto es lo único que un atacante NO puede reproducir sin la clave.
    """
    return hmac.new(
        key=secret_key.encode("utf-8"),
        msg=payload_b64.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()


def generar_licencia(
    cliente: str,
    plan: str,
    dias_validez: int,
    secret_key: str,
) -> str:
    """
    Genera un código de licencia firmado.
    SOLO vos ejecutás esta función, nunca debe estar disponible dentro
    de la app que le entregás al comprador — si el atacante encuentra esta
    función en el código instalado, puede llamarla directamente y generar
    licencias infinitas. Va en tu propia herramienta interna (management
    command, ver generar_licencia.py) o en tu servidor privado.

    payload contiene:
      - id: identificador único de esta licencia (para poder revocarla en tu BD)
      - cliente: a quién se la vendiste (para tu propio control)
      - plan: "basico" | "pro" | "premium"
      - exp: timestamp unix de expiración
    """
    payload = {
        "id": str(uuid.uuid4()),
        "cliente": cliente,
        "plan": plan,
        "exp": int(time.time()) + dias_validez * 86400,
        "emit": int(time.time()),
    }
    payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode("utf-8")).decode("utf-8")
    firma = _firmar(payload_b64, secret_key)

    # Formato final: PAYLOAD.FIRMA — separados por un punto, como hace un JWT
    return f"{payload_b64}.{firma}"


def validar_licencia(codigo: str, secret_key: str) -> dict:
    """
    Verifica un código y devuelve el payload si es válido.
    Lanza LicenciaInvalida o LicenciaExpirada si algo no cierra.

    Este es el ÚNICO código relacionado a licencias que SÍ puede viajar
    dentro de la app del cliente, porque solo verifica, no genera.
    """
    try:
        payload_b64, firma_recibida = codigo.strip().split(".")
    except ValueError:
        raise LicenciaInvalida("Formato de código incorrecto")

    firma_esperada = _firmar(payload_b64, secret_key)

    # hmac.compare_digest en vez de "firma_recibida == firma_esperada":
    # una comparación normal de strings corta apenas encuentra la primera
    # diferencia de caracteres, y el tiempo que tarda en responder revela
    # cuántos caracteres acertó el atacante (timing attack). compare_digest
    # siempre tarda lo mismo, sin importar en qué carácter falla.
    if not hmac.compare_digest(firma_recibida, firma_esperada):
        raise LicenciaInvalida("Firma inválida: el código fue alterado o no fue emitido por este sistema")

    try:
        payload_json = base64.urlsafe_b64decode(payload_b64.encode("utf-8"))
        payload = json.loads(payload_json)
    except Exception:
        raise LicenciaInvalida("No se pudo decodificar el contenido del código")

    if payload["exp"] < time.time():
        raise LicenciaExpirada(f"La licencia venció el {time.ctime(payload['exp'])}")

    return payload
