from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import os

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('', include('usuarios.urls')),  # Tus URLs de la app usuarios
]

# Archivos estáticos y media en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Servir laboratorios directamente desde la carpeta local
LABORATORIOS_DIR = os.path.join('C:', 'home', 'usuario', 'Simuladorfisica', 'laboratorios')
urlpatterns += static('/laboratorios/', document_root=LABORATORIOS_DIR)
