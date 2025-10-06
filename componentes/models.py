from django.db import models
from usuarios.models import Laboratorio

class Component(models.Model):
    nombre = models.CharField("Nombre del componente", max_length=200)
    modelo_3d = models.FileField("Modelo 3D (.glb, .usdz, ...)", upload_to='modelos_3d/', blank=True, null=True)
    imagen = models.ImageField("Imagen del componente", upload_to='componentes_imgs/', blank=True, null=True)
    descripcion = models.TextField("Descripción", blank=True)
    especificaciones = models.TextField("Especificaciones técnicas", blank=True)  # Ejemplo: peso: 1kg, material: plástico
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE, related_name='componentes')
    video_youtube = models.URLField("Video YouTube (URL)", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Componente"
        verbose_name_plural = "Componentes"

    def __str__(self):
        return self.nombre
