from django.db import models
from django.contrib.auth.models import User

class Pago(models.Model):
    usuario = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(auto_now_add=True)
    flight_id = models.IntegerField()  # Elimina max_length
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    fecha_salida = models.CharField(max_length=100)
    fecha_llegada = models.CharField(max_length=100)
