"""
middleware.py — Se ejecuta en CADA request antes de llegar a tu vista.

QUÉ HACE Y POR QUÉ ACÁ Y NO EN CADA VISTA:
Podrías poner un chequeo de licencia al principio de cada view, pero eso
significa acordarte de hacerlo en las 40 vistas que tenga el sistema, y
alcanza con que te olvides una vez para dejar un agujero. El middleware
intercepta TODO antes de que llegue a ninguna vista: es un único punto
de control, imposible de saltear por descuido.

POR QUÉ HAY CACHE:
Validar la firma HMAC es barato (microsegundos), pero igual no tiene
sentido repetir la misma verificación en cada uno de los cientos de
requests que recibe un local en un día. Guardamos el resultado en el
cache de Django por unas horas. Esto también es una decisión de UX: si
revocás una licencia desde el admin, el corte de acceso tarda como
máximo el tiempo del cache, no es instantáneo — es un trade-off
consciente entre carga del servidor y "tiempo de reacción" del bloqueo.
"""

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render
from django.utils import timezone

from .crypto import validar_licencia, LicenciaInvalida, LicenciaExpirada
from .models import Licencia
from .planes import PLANES

CACHE_KEY = "licencia_activa_validada"
CACHE_TIMEOUT_SEGUNDOS = 6 * 60 * 60  # 6 horas


def _validar_desde_cero():
    """
    Hace la verificación completa: firma + registro en base de datos.
    Devuelve un dict con el resultado, nunca lanza excepción (para que
    el middleware nunca rompa el sitio entero por un error acá).
    """
    codigo = getattr(settings, "LICENCIA_CODIGO_ACTIVO", None)
    secret = getattr(settings, "LICENCIA_SECRET_KEY", None)

    if not codigo or not secret:
        return {"valida": False, "motivo": "No hay licencia configurada en este servidor."}

    # Paso 1: la firma. Esto NO requiere base de datos, es matemática pura.
    try:
        payload = validar_licencia(codigo, secret)
    except LicenciaExpirada as e:
        return {"valida": False, "motivo": str(e)}
    except LicenciaInvalida as e:
        return {"valida": False, "motivo": str(e)}

    # Paso 2: el registro administrativo. Acá es donde una revocación manual
    # (activa=False) corta el acceso aunque la firma siga siendo "correcta".
    try:
        registro = Licencia.objects.get(licencia_id=payload["id"])
    except Licencia.DoesNotExist:
        return {"valida": False, "motivo": "La licencia no está registrada en este sistema."}

    if not registro.activa:
        return {"valida": False, "motivo": "La licencia fue desactivada."}

    if registro.fecha_expiracion < timezone.now():
        return {"valida": False, "motivo": "La licencia venció."}

    return {
        "valida": True,
        "plan": payload["plan"],
        "cliente": payload["cliente"],
        "dias_restantes": registro.dias_restantes(),
    }


def obtener_estado_licencia() -> dict:
    """Punto de entrada con cache. Esto es lo que usan el middleware y los templates."""
    resultado = cache.get(CACHE_KEY)
    if resultado is None:
        resultado = _validar_desde_cero()
        cache.set(CACHE_KEY, resultado, CACHE_TIMEOUT_SEGUNDOS)
    return resultado


class LicenciaMiddleware:
    """
    Instalar en settings.MIDDLEWARE. Adjunta request.licencia con el estado
    actual, y bloquea el acceso a rutas protegidas si no es válida.

    RUTAS EXENTAS: la del propio aviso de licencia inválida, y el admin
    (para que siempre puedas entrar a revisar/renovar aunque el resto
    esté bloqueado).
    """

    RUTAS_EXENTAS = ("/admin", "/licencia-invalida")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        estado = obtener_estado_licencia()
        request.licencia = estado

        if not estado["valida"] and not request.path.startswith(self.RUTAS_EXENTAS):
            return render(
                request,
                "licencias/licencia_invalida.html",
                {"motivo": estado.get("motivo", "Licencia no válida.")},
                status=403,
            )

        # Dejamos disponibles los datos del plan activo para toda la request,
        # así las vistas y templates no tienen que volver a buscarlo.
        if estado["valida"]:
            request.plan_info = PLANES.get(estado["plan"], {})
        else:
            request.plan_info = {}

        return self.get_response(request)
