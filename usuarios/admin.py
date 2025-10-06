from django.contrib import admin
from .models import Laboratorio

@admin.register(Laboratorio)
class LaboratorioAdmin(admin.ModelAdmin):
	list_display = ('id', 'nombre_simulacion', 'estado', 'fecha_creacion')
