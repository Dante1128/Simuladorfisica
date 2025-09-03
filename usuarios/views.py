from .forms import CuentaClienteForm, RegistroUsuarioForm
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from .models import Usuario  
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator

def index(request):
    return render(request, 'paginaWeb/index.html')
def base_cliente(request):
    return render(request, 'cliente/baseCliente.html')

def registro_usuario(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.contrasena = make_password(form.cleaned_data["contrasena"])
            usuario.save()
            messages.success(request, "¡Registro exitoso! Ya puedes iniciar sesión.")
            return redirect('login')
        else:
            # Mostrar errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = RegistroUsuarioForm()

    return render(request, 'paginaWeb/registro.html', {"form": form})

from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Usuario 





def home_cliente(request):
    usuario_id = request.session.get('usuario_id')
    usuario = None
    
    if usuario_id:
        try:
            usuario = Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            # Si el usuario no existe en la base de datos, redirigir al login
            request.session.flush()  # Limpiar la sesión en caso de que el ID sea inválido
            messages.error(request, "La sesión ha caducado o el usuario no existe.")
            return redirect('login')
    
    if usuario:
        return render(request, 'cliente/homeCliente.html', {"usuario": usuario})
    else:
        # Si no hay usuario en la sesión, redirigir al login
        return redirect('login')     



def login(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')

        # Validar campos vacíos
        if not correo or not contrasena:
            messages.error(request, "Todos los campos son obligatorios")
            return render(request, 'registration/login.html', {'correo': correo})  # Se pasan los datos ingresados

        # Validar si el correo existe
        usuario = Usuario.objects.filter(correo=correo).first()
        if not usuario:
            messages.error(request, "El correo ingresado no está registrado")
            return render(request, 'registration/login.html', {'correo': correo})

        # Validar contraseña
        if not check_password(contrasena, usuario.contrasena):
            messages.error(request, "La contraseña es incorrecta")
            return render(request, 'registration/login.html', {'correo': correo})

        # Si todo es correcto, guardar sesión
        request.session['usuario_id'] = usuario.id
        return redirect('home_cliente')  

    return render(request, 'registration/login.html')

@login_required(login_url='/login/')
def cuenta_cliente(request):
    # Obtener usuario de la sesión
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, "No has iniciado sesión.")
        return redirect('login')
    usuario = Usuario.objects.get(id=usuario_id)
    if request.method == 'POST':
        form = CuentaClienteForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('cuenta_cliente')  
    else:
        form = CuentaClienteForm(instance=usuario)
    return render(request, 'cliente/cuentaCliente.html', {'usuario': usuario, 'form': form})

from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect
from django.contrib import messages

def logout(request):
    """
    Cierra la sesión del usuario y lo redirige al login.
    """
    # Cerrar sesión del usuario
    auth_logout(request)
    
    # Mostrar mensaje de éxito
    messages.success(request, "Sesión cerrada correctamente.")
    
    # Redirigir al login
    return redirect('login')
    
    # Redirigir al login
    return redirect('login')
