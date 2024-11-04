from django.db import models

# Create your models here.

class Vuelo(models.Model):
    departure_city = models.CharField(max_length=100)
    arrival_city = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.departure_city} a {self.arrival_city} - {self.price}"
