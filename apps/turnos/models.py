from django.db import models


class Barbero(models.Model):
    """
    Modelo para la lista de barberos precargada, tal como se solicita
    en el flujo del sistema.
    """
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100, blank=True)

    # NUEVO: porcentaje que se lleva el barbero de cada servicio que cobra.
    # Va acá (no en Servicio ni en Pago) porque la comisión es una condición
    # laboral del barbero, no del servicio: dos barberos pueden cobrar el
    # mismo corte y llevarse porcentajes distintos según su acuerdo.
    porcentaje_comision = models.DecimalField(
        max_digits=5, decimal_places=2, default=50.00,
        help_text="Porcentaje (0-100) que se lleva este barbero de cada servicio cobrado.",
    )

    def __str__(self):
        return self.nombre


class Servicio(models.Model):
    """
    NUEVO. Sin esto no existe caja ni comisiones: no hay "qué se cobra".
    """
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion_minutos = models.PositiveIntegerField(default=30)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} (${self.precio})"


class Cliente(models.Model):
    """
    NUEVO. Antes el nombre/celular del cliente vivía suelto adentro de cada
    Turno, como texto libre. El problema de eso: "Juan Perez" y "juan perez"
    quedan como dos personas distintas para el sistema, y no hay forma de
    preguntarle a la base de datos "¿cuántas veces vino este cliente?" sin
    comparar strings a mano. Con un modelo propio, el Turno apunta a UN
    Cliente (ForeignKey), y ahí sí la pregunta se responde con una consulta
    directa: Turno.objects.filter(cliente=x).count()
    """
    nombre = models.CharField(max_length=150)
    celular = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, default="")
    acepta_promociones = models.BooleanField(
        default=False,
        verbose_name="Acepta recibir promociones y novedades",
    )
    creado_el = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.celular})"

    def total_visitas(self) -> int:
        return self.turno_set.filter(estado="atendido").count()


class Turno(models.Model):
    """
    Modelo para gestionar las citas. Utiliza el Django ORM para
    consultas seguras y eficientes.
    """

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('atendido', 'Atendido'),
    ]

    # --- Campos originales, sin tocar ---
    # Los dejamos tal cual para no romper nada de lo que ya está en producción.
    # cliente_nombre y cliente_celular quedan como estaban.
    cliente_nombre = models.CharField(max_length=150)
    cliente_celular = models.CharField(max_length=20)

    # --- NUEVO: FK a Cliente, nullable a propósito ---
    # nullable=True porque los turnos que YA existen en tu base de datos de
    # producción no tienen un Cliente asociado todavía. Si esto fuera
    # obligatorio, la migración fallaría al querer aplicarse sobre filas
    # existentes sin saber qué poner ahí. La migración de datos (0003) es
    # la que rellena este campo para los turnos viejos.
    cliente = models.ForeignKey(
        Cliente, on_delete=models.SET_NULL, null=True, blank=True,
    )

    barbero = models.ForeignKey(Barbero, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()

    # NUEVO: qué servicio corresponde a este turno. Nullable por la misma
    # razón que 'cliente': los turnos viejos no tenían este dato.
    servicio = models.ForeignKey(
        Servicio, on_delete=models.SET_NULL, null=True, blank=True,
    )

    estado = models.CharField(max_length=20, choices=ESTADOS, default='confirmado')
    creado_el = models.DateTimeField(auto_now_add=True)

    acepta_promociones = models.BooleanField(
        default=False,
        verbose_name="Acepta recibir promociones y novedades",
    )

    def __str__(self):
        return f"{self.cliente_nombre} - {self.fecha_hora}"


class Pago(models.Model):
    """
    NUEVO. Registra el cobro real de un turno atendido. Es la base de la
    caja y, por extensión, de las comisiones y reportes.

    Por qué es un modelo separado y no simplemente un campo 'monto' en
    Turno: un turno puede quedar 'pendiente' o cancelarse sin que se cobre
    nunca. Mezclar "la cita" con "el cobro" en la misma fila obliga a usar
    campos nulos para representar "todavía no se cobró", lo cual es más
    frágil que simplemente no crear la fila de Pago hasta que el cobro
    efectivamente ocurre.

    Por qué 'monto' se guarda acá en vez de leer Servicio.precio en el
    momento de mostrar un reporte: si mañana subís el precio del corte,
    no querés que cambien retroactivamente los números de facturación de
    meses anteriores. Guardar una "foto" del precio al momento del cobro
    es lo que mantiene la caja histórica exacta.
    """
    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
    ]

    turno = models.OneToOneField(Turno, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default='efectivo')
    fecha_pago = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago ${self.monto} - {self.turno.cliente_nombre}"

    def comision_barbero(self):
        """
        Calcula, al vuelo, cuánto le corresponde al barbero por este pago
        puntual. No se guarda en la base de datos porque si mañana cambiás
        el porcentaje de comisión del barbero, no tiene sentido que los
        pagos viejos "recalculen" solos — pero para el reporte del período
        actual, este cálculo en tiempo real es exactamente lo que querés.
        """
        porcentaje = self.turno.barbero.porcentaje_comision
        return round(self.monto * porcentaje / 100, 2)
