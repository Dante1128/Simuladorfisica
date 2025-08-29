from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.checks import messages
from django.shortcuts import render, redirect
from .forms import RegistroUsuarioForm
from django.contrib.auth.hashers import make_password

def index(request):
    return render(request, 'usuarios/index.html')

def registro_usuario(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit= False)
            usuario.contrasena = make_password(form.cleaned_data["contrasena"])
            usuario.save()
            return redirect('registro')
    else:
         form =  RegistroUsuarioForm()

    return render(request, 'usuarios/registro.html',{"form":form})

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Por favor ingresa todos los campos')
            return render(request, 'usuarios/login.html')
        
        # Buscar usuario por email (ya que Django usa username por defecto)
        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            messages.error(request, 'Credenciales incorrectas')
            return render(request, 'usuarios/login.html')
        
        # Autenticar usuario
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'¡Bienvenido {user.first_name or user.username}!')
                # Redirigir a dashboard o página principal
                return redirect('dashboard')  # Cambia por tu URL de destino
            else:
                messages.error(request, 'Tu cuenta está desactivada')
        else:
            messages.error(request, 'Credenciales incorrectas')
    
    return render(request, 'usuarios/login.html')
