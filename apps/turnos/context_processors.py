from django.conf import settings


def branding(request):
    """
    Inyecta nombre del negocio, logo y colores en TODOS los templates
    automáticamente. Para vender la app a otro cliente: se cambian estas
    4 variables en el .env, no se toca código ni HTML.
    """
    return {
        'nombre_negocio': settings.BRANDING['nombre_negocio'],
        'logo_static_path': settings.BRANDING['logo_static_path'],
        'color_primario': settings.BRANDING['color_primario'],
        'color_acento': settings.BRANDING['color_acento'],
    }
