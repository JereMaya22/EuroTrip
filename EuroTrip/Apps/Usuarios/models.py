from django.db import models

class usurio(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    edad = models.IntegerField(default=18)
    direccion = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    
# Modelo de Aeropuerto
class Aeropuerto(models.Model):
    codigo_aeropuerto = models.CharField(max_length=10)
    ciudad = models.CharField(max_length=100)
    pais = models.CharField(max_length=100)


# Modelo de Vuelo
class Vuelo(models.Model):
    aeropuerto = models.ForeignKey(Aeropuerto, on_delete=models.CASCADE)
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    fecha_llegada = models.DateField()
    fecha_salida = models.DateField()
    hora_llegada = models.TimeField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)



# Modelo de Reserva
class Reserva(models.Model):
    usuario = models.ForeignKey(usurio, on_delete=models.CASCADE)
    vuelo = models.ForeignKey(Vuelo, on_delete=models.CASCADE)
    fecha_reserva = models.DateField(auto_now_add=True)
    numero_asiento = models.CharField(max_length=10)
    clase = models.CharField(max_length=50)



# Modelo de HistorialVuelos
class HistorialVuelos(models.Model):
    usuario = models.ForeignKey(usurio, on_delete=models.CASCADE)
    vuelo = models.ForeignKey(Vuelo, on_delete=models.CASCADE)
    fecha_llegada = models.DateField()
    fecha_salida = models.DateField()



# Modelo de Pago
class Pago(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=50)
