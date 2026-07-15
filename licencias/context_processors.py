"""
context_processors.py — Hace disponible {{ plan }} y sus colores en CUALQUIER
template sin tener que pasarlo a mano en cada vista.

Se registra en TEMPLATES -> OPTIONS -> context_processors (ver integración.md).
Django lo ejecuta antes de renderizar cada template y mergea lo que devuelve
con el resto del contexto.
"""

def info_licencia(request):
    licencia = getattr(request, "licencia", {})
    plan_info = getattr(request, "plan_info", {})
    return {
        "licencia_valida": licencia.get("valida", False),
        "licencia_plan": licencia.get("plan"),
        "licencia_dias_restantes": licencia.get("dias_restantes"),
        "color_primario": plan_info.get("color_primario", "#111827"),
        "color_acento": plan_info.get("color_acento", "#374151"),
        "plan_nombre": plan_info.get("nombre", ""),
    }
