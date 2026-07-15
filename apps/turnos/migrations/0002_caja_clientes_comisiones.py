from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """
    NOTA: 'dependencies' asume que tu migración inicial de turnos se llama
    '0001_initial'. Revisá con `python manage.py showmigrations turnos`
    y ajustá el nombre si es distinto antes de correr `migrate`.

    Esta migración es segura para producción porque:
      - cliente y servicio en Turno son nullable (null=True): las filas
        existentes quedan con NULL ahí, no falla nada.
      - Servicio, Cliente y Pago son tablas NUEVAS: no tocan datos previos.
      - porcentaje_comision en Barbero tiene default=50.00: las filas
        existentes de Barbero se completan automáticamente con ese valor.
    """

    dependencies = [
        ('turnos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='barbero',
            name='porcentaje_comision',
            field=models.DecimalField(
                decimal_places=2, default=50.00, max_digits=5,
                help_text="Porcentaje (0-100) que se lleva este barbero de cada servicio cobrado.",
            ),
        ),
        migrations.CreateModel(
            name='Servicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('duracion_minutos', models.PositiveIntegerField(default=30)),
                ('activo', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150)),
                ('celular', models.CharField(max_length=20, unique=True)),
                ('email', models.EmailField(blank=True, default='', max_length=254)),
                ('acepta_promociones', models.BooleanField(default=False, verbose_name='Acepta recibir promociones y novedades')),
                ('creado_el', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='turno',
            name='cliente',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                to='turnos.cliente',
            ),
        ),
        migrations.AddField(
            model_name='turno',
            name='servicio',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                to='turnos.servicio',
            ),
        ),
        migrations.CreateModel(
            name='Pago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('metodo_pago', models.CharField(choices=[('efectivo', 'Efectivo'), ('tarjeta', 'Tarjeta'), ('transferencia', 'Transferencia')], default='efectivo', max_length=20)),
                ('fecha_pago', models.DateTimeField(auto_now_add=True)),
                ('turno', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='turnos.turno')),
            ],
        ),
    ]
