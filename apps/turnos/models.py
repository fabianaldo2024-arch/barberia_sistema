from django.db import models

class Barbero(models.Model):
    """
    Modelo para la lista de barberos precargada, tal como se solicita
    en el flujo del sistema.
    """
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nombre

class Turno(models.Model):
    """
    Modelo para gestionar las citas. Utiliza el Django ORM para 
    consultas seguras y eficientes.
    """
    
    # Estados definidos en la especificación funcional
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('atendido', 'Atendido'),
    ]

    # Datos obligatorios del cliente según el flujo del sistema
    cliente_nombre = models.CharField(max_length=150)
    cliente_celular = models.CharField(max_length=20) # Debe incluir código de área
    
    # Detalles de la cita
    barbero = models.ForeignKey(Barbero, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()
    
    # Estado del turno para el panel de control de la recepcionista
    estado = models.CharField(max_length=20, choices=ESTADOS, default='confirmado')
    creado_el = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cliente_nombre} - {self.fecha_hora}"