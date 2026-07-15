from django.db import migrations


def poblar_clientes(apps, schema_editor):
    """
    MIGRACIÓN DE DATOS — distinta de una migración de esquema (0002).
    Una migración de esquema le dice a la base "creá esta tabla, agregá esta
    columna". Una migración de DATOS ejecuta código Python que TRANSFORMA
    filas ya existentes. Django las corre igual, en orden, con `migrate`.

    apps.get_model(...) en vez de importar Turno/Cliente directamente:
    esto es a propósito. Las migraciones deben usar una "foto congelada"
    del modelo tal como era EN ESE MOMENTO del historial de migraciones,
    no el modelo actual del archivo models.py (que en el futuro puede
    tener más campos y romper esta migración vieja si se ejecuta desde cero
    en un servidor nuevo).
    """
    Turno = apps.get_model('turnos', 'Turno')
    Cliente = apps.get_model('turnos', 'Cliente')

    for turno in Turno.objects.filter(cliente__isnull=True):
        celular = (turno.cliente_celular or "").strip()
        if not celular:
            continue  # no hay forma de identificar/deduplicar sin celular

        cliente, creado = Cliente.objects.get_or_create(
            celular=celular,
            defaults={
                "nombre": turno.cliente_nombre,
                "acepta_promociones": turno.acepta_promociones,
            },
        )
        turno.cliente = cliente
        turno.save(update_fields=["cliente"])


def revertir(apps, schema_editor):
    # No hace falta borrar los Clientes creados al revertir: son datos
    # válidos igual. Solo dejamos el paso vacío para que Django permita
    # el rollback de esta migración sin error.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('turnos', '0002_caja_clientes_comisiones'),
    ]

    operations = [
        migrations.RunPython(poblar_clientes, revertir),
    ]
