"""
planes.py — Qué desbloquea cada plan y cómo se ve.

DECISIÓN DE DISEÑO IMPORTANTE:
No creamos 3 apps Django distintas ni 3 repos. Un solo código base, y el
PLAN activo (que viene de la licencia validada) decide dos cosas:
  1. Qué funciones están habilitadas (lo controla el decorador requiere_feature)
  2. Qué colores usa el template (lo inyecta el context processor)

Esto es mantenible: arreglás un bug una sola vez, no tres veces.
Es vendible igual: el cliente que paga Básico ve una interfaz celeste
simple; el que paga Premium ve otra paleta y otras opciones de menú.
"""

PLANES = {
    "basico": {
        "nombre": "Básico",
        "color_primario": "#2563EB",
        "color_acento": "#1E40AF",
        "features": {
            "turnos", "caja", "clientes",
        },
    },
    "pro": {
        "nombre": "Pro",
        "color_primario": "#D97706",
        "color_acento": "#92400E",
        "features": {
            "turnos", "caja", "clientes",
            "reportes", "notificaciones",
        },
    },
    "premium": {
        "nombre": "Premium",
        "color_primario": "#111827",
        "color_acento": "#374151",
        "features": {
            "turnos", "caja", "clientes",
            "reportes", "notificaciones",
            "comisiones", "multi_sucursal",
        },
    },
}


def tiene_feature(plan: str, feature: str) -> bool:
    """
    True si el plan dado incluye esa funcionalidad.
    Si el plan no existe (dato corrupto, licencia rara), no habilita nada:
    fallar cerrado (denegar por defecto) es la postura segura, nunca al revés.
    """
    return feature in PLANES.get(plan, {}).get("features", set())
