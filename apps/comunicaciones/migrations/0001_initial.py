from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('turnos', '0002_caja_clientes_comisiones'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('canal', models.CharField(choices=[('email', 'Email'), ('whatsapp', 'WhatsApp'), ('sms', 'SMS')], max_length=20)),
                ('enviado_el', models.DateTimeField(auto_now_add=True)),
                ('exitoso', models.BooleanField(default=True)),
                ('detalle_error', models.TextField(blank=True, default='')),
                ('turno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='turnos.turno')),
            ],
            options={
                'unique_together': {('turno', 'canal')},
            },
        ),
    ]
