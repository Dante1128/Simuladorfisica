from django.contrib import admin
from .models import Component


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'laboratorio')
    search_fields = ('nombre',)
    list_filter = ('laboratorio',)

