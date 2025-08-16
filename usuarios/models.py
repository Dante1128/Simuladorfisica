# usuarios/models.py
from django.db import models

class Usuario(models.Model):
    TIPO_USUARIO = [
        ('estudiante', 'Estudiante'),
        ('universitario', 'Universitario'),
        ('profesional', 'Profesional'),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=128)
    tipo = models.CharField(max_length=20, choices=TIPO_USUARIO, default='estudiante')

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.correo}) - {self.tipo}"
