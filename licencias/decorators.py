"""
decorators.py — Protege una vista puntual según lo que habilita el plan.

El middleware ya te asegura que HAY una licencia válida. Este decorador
resuelve el segundo problema: un cliente con plan Básico no debería poder
entrar a /reportes/ aunque su licencia esté al día, porque esa función
es de plan Pro para arriba.

USO:
    @requiere_feature("reportes")
    def vista_reportes(request):
        ...
"""

from functools import wraps
from django.shortcuts import render

from .planes import tiene_feature


def requiere_feature(feature: str):
    def decorador(vista_func):
        @wraps(vista_func)
        def wrapper(request, *args, **kwargs):
            plan = getattr(request, "licencia", {}).get("plan")
            if not plan or not tiene_feature(plan, feature):
                return render(
                    request,
                    "licencias/feature_bloqueada.html",
                    {"feature": feature},
                    status=402,  # 402 Payment Required — semánticamente correcto acá
                )
            return vista_func(request, *args, **kwargs)
        return wrapper
    return decorador
