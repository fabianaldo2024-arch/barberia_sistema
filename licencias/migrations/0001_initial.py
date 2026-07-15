import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Licencia",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo", models.TextField(unique=True, help_text="El código firmado completo (payload.firma) entregado al cliente.")),
                ("licencia_id", models.UUIDField(help_text="Extraído del payload al generar el código; permite buscarlo sin decodificar todo.")),
                ("cliente", models.CharField(max_length=200)),
                ("plan", models.CharField(choices=[("basico", "Básico"), ("pro", "Pro"), ("premium", "Premium")], max_length=20)),
                ("fecha_emision", models.DateTimeField(auto_now_add=True)),
                ("fecha_expiracion", models.DateTimeField(help_text="Debe coincidir con el 'exp' firmado dentro del código; se guarda también acá para poder filtrar/reportar en el admin sin decodificar.")),
                ("activa", models.BooleanField(default=True, help_text="Apagalo para revocar el acceso al instante, aunque la firma y la fecha sigan siendo válidas.")),
                ("fingerprint_instalacion", models.CharField(blank=True, default="", help_text="Se completa automáticamente la primera vez que la licencia se activa con éxito.", max_length=128)),
                ("notas", models.TextField(blank=True, default="")),
            ],
            options={
                "verbose_name": "Licencia",
                "verbose_name_plural": "Licencias",
                "ordering": ["-fecha_emision"],
            },
        ),
    ]
