from django.db import models
from django.contrib.auth.models import User

class Servicio(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion_minutos = models.IntegerField(help_text="Duración del servicio en minutos")

    def __str__(self):
        return self.nombre

class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    ]

    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    clienta = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas')
    fecha_hora = models.DateTimeField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    
    class Meta:
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"Reserva de {self.servicio.nombre} para {self.clienta.username} el {self.fecha_hora.strftime('%d-%m-%Y %H:%M')}"