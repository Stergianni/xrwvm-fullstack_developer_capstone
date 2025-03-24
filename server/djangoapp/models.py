from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class CarMake(models.Model):
    """
    Modelo que representa una marca de automóvil.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class CarModel(models.Model):
    """
    Modelo que representa un modelo de automóvil asociado a una marca.
    """
    car_make = models.ForeignKey(
        CarMake, on_delete=models.CASCADE
    )  # Relación muchos a uno
    name = models.CharField(max_length=100)

    CAR_TYPES = [
        ('SEDAN', 'Sedan'),
        ('SUV', 'SUV'),
        ('WAGON', 'Wagon'),
        ('HATCHBACK', 'Hatchback'),
        ('CONVERTIBLE', 'Convertible'),
    ]

    type = models.CharField(max_length=15, choices=CAR_TYPES, default='SUV')
    year = models.IntegerField(
        validators=[
            MinValueValidator(2015),  # Año mínimo permitido
            MaxValueValidator(2025),  # Año máximo permitido
        ]
    )
    dealer_id = models.PositiveIntegerField()  # ID del concesionario

    def __str__(self):
        return f"{self.car_make.name} {self.name} ({self.year})"
