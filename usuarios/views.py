from .forms import RegistroUsuarioForm
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from .models import Usuario  

def index(request):
    return render(request, 'paginaWeb/index.html')

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

def login(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')

        # Validar campos vacíos
        if not correo or not contrasena:
            messages.error(request, "Todos los campos son obligatorios")
            return render(request, 'paginaWeb/login.html')

        # Validar si el correo existe
        usuario = Usuario.objects.filter(correo=correo).first()
        if not usuario:
            messages.error(request, "El correo ingresado no está registrado")
            return render(request, 'PaginaWeb/login.html')

        # Validar contraseña
        if not check_password(contrasena, usuario.contrasena):
            messages.error(request, "La contraseña es incorrecta")
            return render(request, 'paginaWeb/login.html')

        # Si todo es correcto, guardar sesión
        request.session['usuario_id'] = usuario.id
        messages.success(request, f"¡Bienvenido {usuario.nombre}!")
        return redirect('home_cliente')

    return render(request, 'paginaWeb/login.html')


def home_cliente(request):
    usuario_id = request.session.get('usuario_id')
    usuario = None
    if usuario_id:
        from .models import Usuario
        usuario = Usuario.objects.get(id=usuario_id)
    return render(request, 'cliente/homeCliente.html', {"usuario": usuario})


