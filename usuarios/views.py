from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from .models import Usuario  
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Laboratorio
from django.utils import timezone

def index(request):
    return render(request, 'paginaWeb/index.html')
def base_cliente(request):
    return render(request, 'cliente/baseCliente.html')
def panel_admin(request):
    """Vista básica para panel de administración"""
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        return render(request, 'administrador/panel_admin.html', {"usuario": usuario})
    except Usuario.DoesNotExist:
        return redirect('login')

def base_admin(request):
    """Vista básica para base de administración"""
    return render(request, 'administrador/base_admin.html')

def perfil_admin(request):
    """Vista básica para perfil de administración"""
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        return render(request, 'administrador/perfil_admin.html', {"usuario": usuario})
    except Usuario.DoesNotExist:
        return redirect('login')


def login(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasenia = request.POST.get('contrasenia')

        # Validar campos vacíos
        if not correo or not contrasenia:
            messages.error(request, "Todos los campos son obligatorios")
            return render(request, 'registration/login.html', {'correo': correo})

        # Buscar usuario por correo
        usuario = Usuario.objects.filter(correo=correo, estado='A').first()
        if not usuario:
            messages.error(request, "El correo ingresado no está registrado o está inactivo")
            return render(request, 'registration/login.html', {'correo': correo})

        # Validar contraseña
        if not check_password(contrasenia, usuario.contrasenia):
            messages.error(request, "La contraseña es incorrecta")
            return render(request, 'registration/login.html', {'correo': correo})

        # Guardar sesión
        request.session['usuario_id'] = usuario.id

        # Redirigir según rol
        if usuario.rol and usuario.rol.tipo.lower() == 'administrador':
            return redirect('panel_admin')  # Panel administrador
        else:
            return redirect('panel_cliente')  # Panel cliente normal

    return render(request, 'registration/login.html')