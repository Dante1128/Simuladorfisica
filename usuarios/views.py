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
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Componente
from .forms import ComponenteForm
from django.shortcuts import get_object_or_404

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


def componentes_list(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    q = request.GET.get('q', '').strip()
    qs = Componente.objects.select_related('tema', 'laboratorio').all()
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(tema__nombre_archivo__icontains=q))

    # paginación simple
    page = request.GET.get('page', 1)
    paginator = Paginator(qs, 12)  # 12 por página
    try:
        componentes_page = paginator.page(page)
    except PageNotAnInteger:
        componentes_page = paginator.page(1)
    except EmptyPage:
        componentes_page = paginator.page(paginator.num_pages)

    context = {
        'componentes': componentes_page,
        'page_obj': componentes_page,
        'paginator': paginator,
        'q': q,
    }
    return render(request, 'administrador/componentes_list.html', context)


def componente_create(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    if request.method == 'POST':
        form = ComponenteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Componente creado correctamente')
            return redirect('componentes_list')
    else:
        form = ComponenteForm()

    return render(request, 'administrador/componente_form.html', {'form': form, 'accion': 'Agregar'})


def componente_update(request, pk):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    componente = get_object_or_404(Componente, pk=pk)
    if request.method == 'POST':
        form = ComponenteForm(request.POST, request.FILES, instance=componente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Componente actualizado correctamente')
            return redirect('componentes_list')
    else:
        form = ComponenteForm(instance=componente)

    return render(request, 'administrador/componente_form.html', {'form': form, 'accion': 'Editar'})


def componente_delete_confirm(request, pk):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    componente = get_object_or_404(Componente, pk=pk)
    if request.method == 'POST':
        componente.delete()
        messages.success(request, 'Componente eliminado')
        return redirect('componentes_list')

    return render(request, 'administrador/componente_confirm_delete.html', {'componente': componente})
    
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