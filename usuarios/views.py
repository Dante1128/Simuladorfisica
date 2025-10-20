# ======================
# IMPORTS DE DJANGO
# ======================
from .views_superadmin_componentes import (
    superadmin_componentes_list,
    superadmin_componente_create,
    superadmin_componente_update,
    superadmin_componente_delete_confirm
)
from .views_superadmin_componentes import (
    superadmin_componente_form_partial,
)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Componente
from .forms import ComponenteForm
from django.shortcuts import get_object_or_404
from .models import Laboratorio
from .forms import LaboratorioForm
import zipfile, os
from django.conf import settings
from django.utils.text import slugify
from django.http import Http404
from .models import Colegio
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Sum
from django.db import models
from django.contrib.admin.views.decorators import staff_member_required

# ======================
# IMPORTS DE MODELOS
# ======================
from .models import (
    Usuario, Persona, Colegio, Estudiante, Profesor, Administrador,
    Suscripcion, Membresia, Curso, Temas, Laboratorio, Componente,
    Pago, Rol, Documento
)

# ======================
# IMPORTS DE FORMULARIOS
# ======================
from .forms import ComponenteForm

# ======================
# IMPORTS DE UTILIDADES / LIBRERÍAS EXTERNAS
# ======================
import csv
import json
import io
import base64
from datetime import datetime
from django.db import models
import mimetypes
import shutil

# ======================
# IMPORTS DE REPORTLAB (PDF)
# ======================
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

import io
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q
import base64
from .models import Documento  
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
import json
from django.http import FileResponse
from django.urls import reverse

def index(request):
    return render(request, 'paginaWeb/index.html')

def base_cliente(request):
    return render(request, 'cliente/baseCliente.html')

#===========================================
#LOGIN
#====================================================================
def login_view(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasenia = request.POST.get('contrasenia')

        # Validar campos vacíos
        if not correo or not contrasenia:
            messages.error(request, "Todos los campos son obligatorios")
            return render(request, 'registration/login.html', {'correo': correo})

        # Buscar usuario por correo
        usuario = Usuario.objects.filter(correo=correo, estado='Activo').first()
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
        if usuario.rol and usuario.rol.tipo:
            # Obtener el tipo de rol y eliminar espacios
            rol_tipo = usuario.rol.tipo.strip()
            
            # Comparar con los valores exactos de la base de datos (camelCase)
            if rol_tipo == 'SuperAdmin':
                return redirect('dashboard_superadmin')
            elif rol_tipo == 'Administrador':
                return redirect('dashboard_administrador')
            elif rol_tipo == 'Profesor':
                return redirect('dashboard_profesor')
            elif rol_tipo == 'Estudiante':
                return redirect('dashboard_estudiante')
            else:
                messages.error(request, f'Rol no reconocido: {usuario.rol.tipo}')
                return render(request, 'registration/login.html')
        else:
            messages.error(request, 'El usuario no tiene rol asignado.')
            return render(request, 'registration/login.html')
        
    # Si no es POST, mostrar el formulario de login
    return render(request, 'registration/login.html')


#====================================================================
#SUPERADMINISTRADOR
#====================================================================
def panel_superadmin(request):
    """Vista básica para panel de administración"""
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        return render(request, 'superadministrador/panel_superadmin.html', {"usuario": usuario})
    except Usuario.DoesNotExist:
        return redirect('login')

def base_superadmin(request):
    """Vista básica para base de administración"""
    return render(request, 'administrador/base_admin.html')

def gestion_colegios(request):
    # CAMBIO DE ESTADO
    estado_id = request.GET.get('estado_id')
    if estado_id:
        try:
            colegio = Colegio.objects.get(id=estado_id)
            colegio.estado = 'Inactivo' if colegio.estado == 'Activo' else 'Activo'
            colegio.save()
            messages.success(request, f'Estado del colegio "{colegio.nombre}" actualizado a {colegio.estado}.')
        except Colegio.DoesNotExist:
            messages.error(request, 'Colegio no encontrado.')
        return HttpResponse(status=204)

    # CREAR COLEGIO
    if request.method == 'POST' and 'crear' in request.POST:
        nombre = request.POST.get('nombre', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        if nombre and direccion:
            if not Colegio.objects.filter(nombre__iexact=nombre).exists():
                Colegio.objects.create(nombre=nombre, direccion=direccion)
                messages.success(request, 'Colegio creado correctamente.')
            else:
                messages.error(request, 'Ya existe un colegio con ese nombre.')
        else:
            messages.error(request, 'Todos los campos son obligatorios.')

    # EDITAR COLEGIO
    if request.method == 'POST' and 'editar_id' in request.POST:
        editar_id = request.POST.get('editar_id')
        nombre = request.POST.get('editar_nombre', '').strip()
        direccion = request.POST.get('editar_direccion', '').strip()
        colegio = Colegio.objects.filter(id=editar_id).first()
        if colegio and nombre and direccion:
            if not Colegio.objects.filter(nombre__iexact=nombre).exclude(id=editar_id).exists():
                colegio.nombre = nombre
                colegio.direccion = direccion
                colegio.save()
                messages.success(request, 'Colegio editado correctamente.')
            else:
                messages.error(request, 'Ya existe un colegio con ese nombre.')
        else:
            messages.error(request, 'Todos los campos son obligatorios para editar.')

    # FILTRO
    search_term = request.GET.get('search', '').strip()
    if search_term:
        colegios = Colegio.objects.filter(
            Q(nombre__icontains=search_term) | Q(direccion__icontains=search_term)
        ).order_by('-id')  
    else:
        colegios = Colegio.objects.all().order_by('-id')  

    return render(request, 'superadministrador/gestion_colegios.html', {'colegios': colegios})


def gestion_administradores(request):
    administradores = Administrador.objects.all().select_related('usuario', 'persona', 'colegio')
    colegios = Colegio.objects.filter(estado='Activo')

    # ===========================
    # CREAR ADMINISTRADOR
    # ===========================
    if request.method == "POST" and request.POST.get('crear') == '1':
        correo = request.POST.get('correo')
        contrasenia = request.POST.get('contrasenia')
        nombre = request.POST.get('nombre')
        apellidoPaterno = request.POST.get('apellidoPaterno')
        apellidoMaterno = request.POST.get('apellidoMaterno')
        colegio_id = request.POST.get('colegio') or None

        try:
            rol_admin = Rol.objects.get(tipo='Administrador')

            usuario = Usuario.objects.create(
                correo=correo,
                contrasenia=make_password(contrasenia),
                estado='Activo',
                rol=rol_admin
            )

            persona = Persona.objects.create(
                usuario=usuario,
                nombre=nombre,
                apellidoPaterno=apellidoPaterno,
                apellidoMaterno=apellidoMaterno,
                estado='Activo'
            )

            Administrador.objects.create(
                usuario=usuario,
                persona=persona,
                colegio_id=colegio_id,
                estado='Activo'
            )

            messages.success(request, "Administrador creado correctamente.")
            return redirect('gestion_administradores')

        except Exception as e:
            messages.error(request, f"Error al crear administrador: {str(e)}")

    # ===========================
    # EDITAR ADMINISTRADOR
    # ===========================
    elif request.method == "POST" and request.POST.get('editar') == '1':
        admin_id = request.POST.get('admin_id')
        admin = get_object_or_404(Administrador, id=admin_id)
        usuario = admin.usuario
        persona = admin.persona

        correo = request.POST.get('correo')
        nombre = request.POST.get('nombre')
        apellidoPaterno = request.POST.get('apellidoPaterno')
        apellidoMaterno = request.POST.get('apellidoMaterno')
        colegio_id = request.POST.get('colegio') or None

        try:
            # Actualizar usuario
            usuario.correo = correo
            usuario.save()

            # Actualizar persona
            persona.nombre = nombre
            persona.apellidoPaterno = apellidoPaterno
            persona.apellidoMaterno = apellidoMaterno
            persona.save()

            # Actualizar administrador
            admin.colegio_id = colegio_id
            admin.save()

            messages.success(request, "Administrador actualizado correctamente.")
            return redirect('gestion_administradores')
        except Exception as e:
            messages.error(request, f"Error al editar administrador: {str(e)}")

    # ===========================
    # CAMBIAR ESTADO ADMINISTRADOR
    # ===========================
    elif request.method == "POST" and request.POST.get('cambiar_estado') == '1':
        admin_id = request.POST.get('admin_id')
        admin = get_object_or_404(Administrador, id=admin_id)
        try:
            admin.estado = 'Inactivo' if admin.estado == 'Activo' else 'Activo'
            admin.save()
            messages.success(request, f"Estado cambiado a {admin.estado} correctamente.")
            return redirect('gestion_administradores')
        except Exception as e:
            messages.error(request, f"Error al cambiar estado: {str(e)}")

    context = {
        'administradores': administradores,
        'colegios': colegios
    }
    return render(request, 'superadministrador/gestion_administradores.html', context)


#====================================================================
# CRUD PROFESORES
#====================================================================

def gestion_profesor(request):
    # CREAR PROFESOR
    if request.method == 'POST' and 'crear' in request.POST:
        nombre = request.POST.get('nombre', '').strip()
        apellidoPaterno = request.POST.get('apellidoPaterno', '').strip()
        apellidoMaterno = request.POST.get('apellidoMaterno', '').strip()
        correo = request.POST.get('correo', '').strip()
        contrasenia = request.POST.get('contrasenia', '').strip()
        colegio_id = request.POST.get('colegio')
        curso = request.POST.get('curso', '').strip()
        if nombre and apellidoPaterno and apellidoMaterno and correo and contrasenia and colegio_id and curso:
            if not Usuario.objects.filter(correo=correo).exists():
                rol_profesor = Rol.objects.get(id=3)
                usuario = Usuario.objects.create(
                    correo=correo,
                    contrasenia=make_password(contrasenia),
                    estado='Activo',
                    rol=rol_profesor
                )
                from .models import Persona
                persona = Persona.objects.create(
                    usuario=usuario,
                    nombre=nombre,
                    apellidoPaterno=apellidoPaterno,
                    apellidoMaterno=apellidoMaterno
                )
                profesor = Profesor.objects.create(
                    usuario=usuario,
                    colegio_id=colegio_id,
                    curso=curso
                )
                messages.success(request, 'Profesor creado correctamente.')
            else:
                messages.error(request, 'Ya existe un usuario con ese correo.')
        else:
            messages.error(request, 'Todos los campos son obligatorios.')

    # EDITAR PROFESOR
    if request.method == 'POST' and 'editar_id' in request.POST:
        editar_id = request.POST.get('editar_id')
        nombre = request.POST.get('editar_nombre', '').strip()
        apellidoPaterno = request.POST.get('editar_apellidoPaterno', '').strip()
        apellidoMaterno = request.POST.get('editar_apellidoMaterno', '').strip()
        correo = request.POST.get('editar_correo', '').strip()
        contrasenia = request.POST.get('editar_contrasenia', '').strip()
        colegio_id = request.POST.get('editar_colegio')
        curso = request.POST.get('editar_curso', '').strip()
        profesor = Profesor.objects.filter(id=editar_id).first()
        if profesor and nombre and apellidoPaterno and apellidoMaterno and correo and colegio_id and curso:
            usuario = profesor.usuario
            if not Usuario.objects.filter(correo=correo).exclude(id=usuario.id).exists():
                usuario.correo = correo
                if contrasenia:
                    usuario.contrasenia = contrasenia
                usuario.save()
                from .models import Persona
                persona = usuario.personas.first()
                if persona:
                    persona.nombre = nombre
                    persona.apellidoPaterno = apellidoPaterno
                    persona.apellidoMaterno = apellidoMaterno
                    persona.save()
                else:
                    Persona.objects.create(
                        usuario=usuario,
                        nombre=nombre,
                        apellidoPaterno=apellidoPaterno,
                        apellidoMaterno=apellidoMaterno
                    )
                profesor.colegio_id = colegio_id
                profesor.curso = curso
                profesor.save()
                messages.success(request, 'Profesor editado correctamente.')
            else:
                messages.error(request, 'Ya existe un usuario con ese correo.')
        else:
            messages.error(request, 'Todos los campos son obligatorios para editar.')

    if request.method == "POST" and request.POST.get('cambiar_estado') == '1':
        profesor_id = request.POST.get('profesor_id')
        profesor = Profesor.objects.filter(id=profesor_id).first()
        if profesor:
            profesor.estado = 'Inactivo' if profesor.estado == 'Activo' else 'Activo'
            profesor.save()
            messages.success(request, f"Estado del profesor cambiado a {profesor.estado}.")
        else:
            messages.error(request, 'Profesor no encontrado.')
        return redirect('gestion_profesor')

    # LISTAR PROFESORES
    profesores = Profesor.objects.select_related('usuario', 'colegio').all().order_by('usuario__correo')
    colegios = Colegio.objects.all().order_by('nombre')
    context = {
        'profesores': profesores,
        'colegios': colegios,
    }
    return render(request, 'superadministrador/gestion_profesor.html', context)


def gestion_estudiante(request):
    estudiantes = Estudiante.objects.all()
    colegios = Colegio.objects.all()

    if request.method == 'POST':
        estudiante_id = request.POST.get('alumno-id')
        nombres = request.POST.get('alumno-nombres')
        apellidos = request.POST.get('alumno-apellidos')
        curso = request.POST.get('alumno-curso')
        colegio_id = request.POST.get('alumno-colegio')
        correo = request.POST.get('alumno-email')
        contrasenia = request.POST.get('alumno-password')

        colegio = get_object_or_404(Colegio, id=colegio_id)

        if estudiante_id:  # Editar estudiante
            estudiante = get_object_or_404(Estudiante, id=estudiante_id)
            # Actualizar persona
            estudiante.persona.nombre = nombres
            estudiante.persona.apellidoPaterno = apellidos.split()[0]
            estudiante.persona.apellidoMaterno = ' '.join(apellidos.split()[1:]) if len(apellidos.split()) > 1 else ''
            estudiante.persona.save()

            # Actualizar usuario
            estudiante.persona.usuario.correo = correo
            if contrasenia:
                estudiante.persona.usuario.contrasenia = make_password(contrasenia)
            estudiante.persona.usuario.save()

            # Actualizar estudiante
            estudiante.curso = curso
            estudiante.colegio = colegio
            estudiante.save()

            messages.success(request, f"Estudiante {estudiante.persona.nombre} actualizado correctamente")

        else:  # Crear nuevo estudiante
            #  Crear usuario primero
            usuario = Usuario.objects.create(
                correo=correo,
                contrasenia=make_password(contrasenia)
                
            )

            #  Crear persona vinculada al usuario
            persona = Persona.objects.create(
                usuario=usuario,
                nombre=nombres,
                apellidoPaterno=apellidos.split()[0],
                apellidoMaterno=' '.join(apellidos.split()[1:]) if len(apellidos.split()) > 1 else ''
            )

            #  Crear estudiante
            Estudiante.objects.create(
                persona=persona,
                colegio=colegio,
                curso=curso
            )

            messages.success(request, f"Estudiante {persona.nombre} registrado correctamente")

        return redirect('gestion_estudiante')

    return render(request, 'superAdministrador/gestion_estudiante.html', {
        'estudiantes': estudiantes,
        'colegios': colegios
    })


#estudiante
def panel_estudiante(request):
    """Vista básica para panel de administración"""
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        return render(request, 'estudiante/panel_estudiante.html', {"usuario": usuario})
    except Usuario.DoesNotExist:
        return redirect('login')

def base_estudiante(request):
    """Vista básica para base de administración"""
    return render(request, 'estudiante/base_estudiante.html')

def perfil_estudiante(request):
    """Vista básica para perfil de administración"""
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        return render(request, 'estudiante/perfil_estudiante.html', {"usuario": usuario})
    except Usuario.DoesNotExist:
        return redirect('login')


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
    return render(request, 'estudiante/base_admin.html')

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
    qs = Componente.objects.select_related('tema', 'laboratorio').all().order_by('nombre')
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
        return render(request, 'estudiante/perfil_admin.html', {"usuario": usuario})
    except Usuario.DoesNotExist:
        return redirect('login')
    
    

def panel_profesor(request):
    # """Vista básica para panel de administración"""
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
       return redirect('login')
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        return render(request, 'profesor/panel_profesor.html', {"usuario": usuario})
    except Usuario.DoesNotExist:
        return redirect('login')

def componentes_estudiante(request):
    """Vista para mostrar componentes a los estudiantes"""
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    # Búsqueda
    q = request.GET.get('q', '').strip()
    qs = Componente.objects.select_related('tema', 'laboratorio').all().order_by('nombre')
    
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(tema__nombre_archivo__icontains=q))

    # Preparar datos para JSON
    componentes_json = []
    for comp in qs:
        componentes_json.append({
            'id': comp.id,
            'nombre': comp.nombre,
            'descripcion': comp.descripcion,
            'especificaciones': comp.especificaciones if hasattr(comp, 'especificaciones') else None,
            'imagen_url': comp.imagen.url if comp.imagen else None,
            'modelo3D_url': comp.modelo3D.url if hasattr(comp, 'modelo3D') and comp.modelo3D else None,
            'video_explicacion': comp.video_explicacion if hasattr(comp, 'video_explicacion') else None,
            'tema_nombre': comp.tema.nombre_archivo if comp.tema else None,
            'laboratorio_nombre': comp.laboratorio.nombre if comp.laboratorio else None
        })

    # Paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(qs, 12)  # 12 componentes por página
    
    try:
        componentes_page = paginator.page(page)
    except PageNotAnInteger:
        componentes_page = paginator.page(1)
    except EmptyPage:
        componentes_page = paginator.page(paginator.num_pages)

    import json
    context = {
        'componentes': componentes_page,
        'componentes_json': json.dumps(componentes_json),
        'page_obj': componentes_page,
        'paginator': paginator,
        'q': q,
    }
    
    return render(request, 'estudiante/componentes_tarjetas.html', context)



### --- VISTAS PARA LABORATORIOS (SUPERADMIN) --- ###
def laboratorios_list(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    labs = Laboratorio.objects.all()
    return render(request, 'superadministrador/laboratorios_list.html', {'laboratorios': labs})


def laboratorio_create(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    if request.method == 'POST':
        form = LaboratorioForm(request.POST, request.FILES)
        if form.is_valid():
            lab = form.save(commit=False)
            lab.save()

            archivo_zip = request.FILES.get('archivo_zip')
            if archivo_zip and zipfile.is_zipfile(archivo_zip):
                target_dir = os.path.join(settings.MEDIA_ROOT, 'laboratorios', str(lab.id))
                os.makedirs(target_dir, exist_ok=True)
                tmp_zip_path = os.path.join(target_dir, f'tmp_{lab.id}.zip')
                with open(tmp_zip_path, 'wb') as f:
                    for chunk in archivo_zip.chunks():
                        f.write(chunk)
                allowed_exts = {'.html', '.htm', '.png', '.jpg', '.jpeg', '.gif', '.css', '.js', '.glb', '.gltf', '.obj', '.mtl', '.bin', '.svg'}
                import shutil as _shutil
                with zipfile.ZipFile(tmp_zip_path, 'r') as z:
                    for member in z.infolist():
                        name = member.filename
                        norm_name = os.path.normpath(name)
                        if norm_name.startswith('..') or os.path.isabs(norm_name):
                            continue
                        if name.endswith('/') or name.endswith('\\'):
                            continue
                        ext = os.path.splitext(name)[1].lower()
                        if ext not in allowed_exts:
                            continue
                        parts = [p for p in name.split('/') if p and p != '..']
                        dest_path = os.path.join(target_dir, *parts)
                        dest_dir = os.path.dirname(dest_path)
                        os.makedirs(dest_dir, exist_ok=True)
                        with z.open(member) as source, open(dest_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
                os.remove(tmp_zip_path)
                rel_path = os.path.join('laboratorios', str(lab.id))
                lab.carpeta = rel_path
                lab.save()

            messages.success(request, 'Laboratorio creado correctamente')
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return HttpResponse('OK')
            return redirect('laboratorios_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return render(request, 'superadministrador/laboratorio_form_modal.html', {'form': form, 'action_url': request.path})
    else:
        form = LaboratorioForm()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return render(request, 'superadministrador/laboratorio_form_modal.html', {'form': form, 'action_url': request.path})

    return render(request, 'superadministrador/laboratorio_form.html', {'form': form, 'accion': 'Agregar'})


def laboratorio_update(request, pk):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    lab = get_object_or_404(Laboratorio, pk=pk)
    if request.method == 'POST':
        form = LaboratorioForm(request.POST, request.FILES, instance=lab)
        if form.is_valid():
            lab = form.save()
            archivo_zip = request.FILES.get('archivo_zip')
            if archivo_zip and zipfile.is_zipfile(archivo_zip):
                target_dir = os.path.join(settings.MEDIA_ROOT, 'laboratorios', str(lab.id))
                os.makedirs(target_dir, exist_ok=True)
                tmp_zip_path = os.path.join(target_dir, f'tmp_{lab.id}.zip')
                with open(tmp_zip_path, 'wb') as f:
                    for chunk in archivo_zip.chunks():
                        f.write(chunk)
                allowed_exts = {'.html', '.htm', '.png', '.jpg', '.jpeg', '.gif', '.css', '.js', '.glb', '.gltf', '.obj', '.mtl', '.bin', '.svg'}
                with zipfile.ZipFile(tmp_zip_path, 'r') as z:
                    for member in z.infolist():
                        name = member.filename
                        norm_name = os.path.normpath(name)
                        if norm_name.startswith('..') or os.path.isabs(norm_name):
                            continue
                        if name.endswith('/') or name.endswith('\\'):
                            continue
                        ext = os.path.splitext(name)[1].lower()
                        if ext not in allowed_exts:
                            continue
                        parts = [p for p in name.split('/') if p and p != '..']
                        dest_path = os.path.join(target_dir, *parts)
                        dest_dir = os.path.dirname(dest_path)
                        os.makedirs(dest_dir, exist_ok=True)
                        with z.open(member) as source, open(dest_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
                os.remove(tmp_zip_path)
                lab.carpeta = os.path.join('laboratorios', str(lab.id))
                lab.save()

            messages.success(request, 'Laboratorio actualizado correctamente')
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return HttpResponse('OK')
            return redirect('laboratorios_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return render(request, 'superadministrador/laboratorio_form_modal.html', {'form': form, 'action_url': request.path})
    else:
        form = LaboratorioForm(instance=lab)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return render(request, 'superadministrador/laboratorio_form_modal.html', {'form': form, 'action_url': request.path})

    return render(request, 'superadministrador/laboratorio_form.html', {'form': form, 'accion': 'Editar', 'laboratorio': lab})


def laboratorio_delete_confirm(request, pk):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    lab = get_object_or_404(Laboratorio, pk=pk)
    if request.method == 'POST':
        # eliminar carpeta y archivo si existen
        if lab.carpeta:
            full_dir = os.path.join(settings.MEDIA_ROOT, lab.carpeta)
            if os.path.exists(full_dir):
                # eliminar recursivamente
                import shutil
                shutil.rmtree(full_dir)
        lab.delete()
        messages.success(request, 'Laboratorio eliminado')
        return redirect('laboratorios_list')

    return render(request, 'superadministrador/laboratorio_confirm_delete.html', {'laboratorio': lab})


### --- VISTAS ESTUDIANTES (INTERFAZ) --- ###
def estudiantes_laboratorios_list(request):
    # lista pública (o basada en sesión) de laboratorios disponibles
    labs = Laboratorio.objects.filter(estado='activo')
    return render(request, 'estudiantes/laboratorios_list.html', {'laboratorios': labs})


def laboratorio_access_confirm(request, pk):
    lab = get_object_or_404(Laboratorio, pk=pk)
    return render(request, 'estudiantes/laboratorio_confirm.html', {'laboratorio': lab})


def laboratorio_entrar(request, pk):
    lab = get_object_or_404(Laboratorio, pk=pk)
    # buscar archivo HTML principal en la carpeta extraída
    if not lab.carpeta:
        raise Http404('El laboratorio no tiene recursos cargados.')

    carpeta_fs = os.path.join(settings.MEDIA_ROOT, lab.carpeta)
    if not os.path.isdir(carpeta_fs):
        raise Http404('Los archivos del laboratorio no existen.')

    # preferir index.html
    index_candidate = os.path.join(carpeta_fs, 'index.html')
    if os.path.exists(index_candidate):
        index_rel = os.path.join(settings.MEDIA_URL, lab.carpeta, 'index.html')
    else:
        # buscar primer .html en la carpeta
        html_files = [f for f in os.listdir(carpeta_fs) if f.lower().endswith('.html')]
        if not html_files:
            raise Http404('No hay archivo HTML en la carpeta del laboratorio.')
        index_rel = os.path.join(settings.MEDIA_URL, lab.carpeta, html_files[0])

    # pasar la URL pública del HTML al template para incrustarlo en un iframe
    # Usar una vista segura para servir los recursos del laboratorio
    if index_candidate and os.path.exists(index_candidate):
        filename = 'index.html'
    else:
        filename = html_files[0]

    html_url = reverse('laboratorio_serve', kwargs={'pk': lab.id, 'filename': filename})
    return render(request, 'estudiantes/laboratorio_view.html', {'laboratorio': lab, 'html_url': html_url})


def laboratorio_serve(request, pk, filename):
    """Sirve archivos de laboratorio de forma segura desde MEDIA_ROOT/<lab.carpeta>/<filename>.
    Evita path traversal y restringe extensiones permitidas.
    """
    lab = get_object_or_404(Laboratorio, pk=pk)
    if not lab.carpeta:
        raise Http404('Recursos no disponibles')

    # normalizar filename y prevenir traversal
    safe_rel = os.path.normpath(filename)
    if safe_rel.startswith('..') or os.path.isabs(safe_rel):
        raise Http404('Archivo no permitido')

    media_base = os.path.abspath(os.path.join(settings.MEDIA_ROOT, lab.carpeta))
    full_path = os.path.abspath(os.path.join(media_base, safe_rel))
    if not full_path.startswith(media_base):
        raise Http404('Acceso denegado')
    if not os.path.exists(full_path):
        raise Http404('Archivo no encontrado')

    allowed_exts = {'.html', '.htm', '.png', '.jpg', '.jpeg', '.gif', '.css', '.js', '.glb', '.gltf', '.obj', '.mtl', '.bin', '.svg'}
    ext = os.path.splitext(full_path)[1].lower()
    if ext not in allowed_exts:
        raise Http404('Tipo de archivo no permitido')

    mime, _ = mimetypes.guess_type(full_path)
    if not mime:
        mime = 'application/octet-stream'

    response = FileResponse(open(full_path, 'rb'), content_type=mime)
    response['X-Content-Type-Options'] = 'nosniff'
    # CSP básica para HTML
    if mime == 'text/html':
        response['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' data: blob:; frame-ancestors 'self';"

    return response


### --- VISTAS PARA LABORATORIOS (SUPERADMIN) --- ###
def laboratorios_list(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    labs = Laboratorio.objects.all()
    return render(request, 'superadministrador/laboratorios_list.html', {'laboratorios': labs})


def laboratorio_create(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    if request.method == 'POST':
        form = LaboratorioForm(request.POST, request.FILES)
        if form.is_valid():
            lab = form.save(commit=False)
            lab.save()

            archivo_zip = request.FILES.get('archivo_zip')
            if archivo_zip and zipfile.is_zipfile(archivo_zip):
                target_dir = os.path.join(settings.MEDIA_ROOT, 'laboratorios', str(lab.id))
                os.makedirs(target_dir, exist_ok=True)
                tmp_zip_path = os.path.join(target_dir, f'tmp_{lab.id}.zip')
                with open(tmp_zip_path, 'wb') as f:
                    for chunk in archivo_zip.chunks():
                        f.write(chunk)
                allowed_exts = {'.html', '.htm', '.png', '.jpg', '.jpeg', '.gif', '.css', '.js', '.glb', '.gltf', '.obj', '.mtl', '.bin', '.svg'}
                import shutil as _shutil
                with zipfile.ZipFile(tmp_zip_path, 'r') as z:
                    for member in z.infolist():
                        name = member.filename
                        norm_name = os.path.normpath(name)
                        if norm_name.startswith('..') or os.path.isabs(norm_name):
                            continue
                        if name.endswith('/') or name.endswith('\\'):
                            continue
                        ext = os.path.splitext(name)[1].lower()
                        if ext not in allowed_exts:
                            continue
                        parts = [p for p in name.split('/') if p and p != '..']
                        dest_path = os.path.join(target_dir, *parts)
                        dest_dir = os.path.dirname(dest_path)
                        os.makedirs(dest_dir, exist_ok=True)
                        with z.open(member) as source, open(dest_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
                os.remove(tmp_zip_path)
                rel_path = os.path.join('laboratorios', str(lab.id))
                lab.carpeta = rel_path
                lab.save()

            messages.success(request, 'Laboratorio creado correctamente')
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return HttpResponse('OK')
            return redirect('laboratorios_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return render(request, 'superadministrador/laboratorio_form_modal.html', {'form': form, 'action_url': request.path})
    else:
        form = LaboratorioForm()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return render(request, 'superadministrador/laboratorio_form_modal.html', {'form': form, 'action_url': request.path})

    return render(request, 'superadministrador/laboratorio_form.html', {'form': form, 'accion': 'Agregar'})


def laboratorio_update(request, pk):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    lab = get_object_or_404(Laboratorio, pk=pk)
    if request.method == 'POST':
        form = LaboratorioForm(request.POST, request.FILES, instance=lab)
        if form.is_valid():
            lab = form.save()
            archivo_zip = request.FILES.get('archivo_zip')
            if archivo_zip and zipfile.is_zipfile(archivo_zip):
                target_dir = os.path.join(settings.MEDIA_ROOT, 'laboratorios', str(lab.id))
                os.makedirs(target_dir, exist_ok=True)
                tmp_zip_path = os.path.join(target_dir, f'tmp_{lab.id}.zip')
                with open(tmp_zip_path, 'wb') as f:
                    for chunk in archivo_zip.chunks():
                        f.write(chunk)
                allowed_exts = {'.html', '.htm', '.png', '.jpg', '.jpeg', '.gif', '.css', '.js', '.glb', '.gltf', '.obj', '.mtl', '.bin', '.svg'}
                with zipfile.ZipFile(tmp_zip_path, 'r') as z:
                    for member in z.infolist():
                        name = member.filename
                        norm_name = os.path.normpath(name)
                        if norm_name.startswith('..') or os.path.isabs(norm_name):
                            continue
                        if name.endswith('/') or name.endswith('\\'):
                            continue
                        ext = os.path.splitext(name)[1].lower()
                        if ext not in allowed_exts:
                            continue
                        parts = [p for p in name.split('/') if p and p != '..']
                        dest_path = os.path.join(target_dir, *parts)
                        dest_dir = os.path.dirname(dest_path)
                        os.makedirs(dest_dir, exist_ok=True)
                        with z.open(member) as source, open(dest_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
                os.remove(tmp_zip_path)
                lab.carpeta = os.path.join('laboratorios', str(lab.id))
                lab.save()

            messages.success(request, 'Laboratorio actualizado correctamente')
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return HttpResponse('OK')
            return redirect('laboratorios_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return render(request, 'superadministrador/laboratorio_form_modal.html', {'form': form, 'action_url': request.path})
    else:
        form = LaboratorioForm(instance=lab)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return render(request, 'superadministrador/laboratorio_form_modal.html', {'form': form, 'action_url': request.path})

    return render(request, 'superadministrador/laboratorio_form.html', {'form': form, 'accion': 'Editar', 'laboratorio': lab})


def laboratorio_delete_confirm(request, pk):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    lab = get_object_or_404(Laboratorio, pk=pk)
    if request.method == 'POST':
        # eliminar carpeta y archivo si existen
        if lab.carpeta:
            full_dir = os.path.join(settings.MEDIA_ROOT, lab.carpeta)
            if os.path.exists(full_dir):
                # eliminar recursivamente
                import shutil
                shutil.rmtree(full_dir)
        lab.delete()
        messages.success(request, 'Laboratorio eliminado')
        return redirect('laboratorios_list')

    return render(request, 'superadministrador/laboratorio_confirm_delete.html', {'laboratorio': lab})


### --- VISTAS ESTUDIANTES (INTERFAZ) --- ###
def estudiantes_laboratorios_list(request):
    # lista pública (o basada en sesión) de laboratorios disponibles
    labs = Laboratorio.objects.filter(estado='activo')
    return render(request, 'estudiantes/laboratorios_list.html', {'laboratorios': labs})


def laboratorio_access_confirm(request, pk):
    lab = get_object_or_404(Laboratorio, pk=pk)
    return render(request, 'estudiantes/laboratorio_confirm.html', {'laboratorio': lab})


def laboratorio_entrar(request, pk):
    lab = get_object_or_404(Laboratorio, pk=pk)
    # buscar archivo HTML principal en la carpeta extraída
    if not lab.carpeta:
        raise Http404('El laboratorio no tiene recursos cargados.')

    carpeta_fs = os.path.join(settings.MEDIA_ROOT, lab.carpeta)
    if not os.path.isdir(carpeta_fs):
        raise Http404('Los archivos del laboratorio no existen.')

    # preferir index.html
    index_candidate = os.path.join(carpeta_fs, 'index.html')
    if os.path.exists(index_candidate):
        index_rel = os.path.join(settings.MEDIA_URL, lab.carpeta, 'index.html')
    else:
        # buscar primer .html en la carpeta
        html_files = [f for f in os.listdir(carpeta_fs) if f.lower().endswith('.html')]
        if not html_files:
            raise Http404('No hay archivo HTML en la carpeta del laboratorio.')
        index_rel = os.path.join(settings.MEDIA_URL, lab.carpeta, html_files[0])

    # pasar la URL pública del HTML al template para incrustarlo en un iframe
    # Usar una vista segura para servir los recursos del laboratorio
    if index_candidate and os.path.exists(index_candidate):
        filename = 'index.html'
    else:
        filename = html_files[0]

    html_url = reverse('laboratorio_serve', kwargs={'pk': lab.id, 'filename': filename})
    return render(request, 'estudiantes/laboratorio_view.html', {'laboratorio': lab, 'html_url': html_url})


def laboratorio_serve(request, pk, filename):
    """Sirve archivos de laboratorio de forma segura desde MEDIA_ROOT/<lab.carpeta>/<filename>.
    Evita path traversal y restringe extensiones permitidas.
    """
    lab = get_object_or_404(Laboratorio, pk=pk)
    if not lab.carpeta:
        raise Http404('Recursos no disponibles')

    # normalizar filename y prevenir traversal
    safe_rel = os.path.normpath(filename)
    if safe_rel.startswith('..') or os.path.isabs(safe_rel):
        raise Http404('Archivo no permitido')

    media_base = os.path.abspath(os.path.join(settings.MEDIA_ROOT, lab.carpeta))
    full_path = os.path.abspath(os.path.join(media_base, safe_rel))
    if not full_path.startswith(media_base):
        raise Http404('Acceso denegado')
    if not os.path.exists(full_path):
        raise Http404('Archivo no encontrado')

    allowed_exts = {'.html', '.htm', '.png', '.jpg', '.jpeg', '.gif', '.css', '.js', '.glb', '.gltf', '.obj', '.mtl', '.bin', '.svg'}
    ext = os.path.splitext(full_path)[1].lower()
    if ext not in allowed_exts:
        raise Http404('Tipo de archivo no permitido')

    mime, _ = mimetypes.guess_type(full_path)
    if not mime:
        mime = 'application/octet-stream'

    response = FileResponse(open(full_path, 'rb'), content_type=mime)
    response['X-Content-Type-Options'] = 'nosniff'
    # CSP básica para HTML
    if mime == 'text/html':
        response['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' data: blob:; frame-ancestors 'self';"

    return response

# ====================================================================
# DECORATOR PERSONALIZADO PARA AUTENTICACIÓN
# ====================================================================
def login_required_custom(view_func):
    def _wrapped_view(request, *args, **kwargs):
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            messages.error(request, 'Debe iniciar sesión')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# ====================================================================
# DASHBOARD SUPERADMINISTRADOR
# ====================================================================
@login_required_custom
def dashboard_superadmin(request):
    usuario_id = request.session.get('usuario_id')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        
        # Verificar que sea superadministrador
        if not usuario.rol or usuario.rol.tipo != 'SuperAdmin':
            messages.error(request, 'No tiene permisos para acceder a esta página')
            return redirect('dashboard_superadmin')

        
        # FILTROS
        fecha_inicio = request.GET.get('fecha_inicio', '')
        fecha_fin = request.GET.get('fecha_fin', '')
        filtro_colegio = request.GET.get('colegio', '')
        
        # Consultas base
        colegios_query = Colegio.objects.all()
        usuarios_query = Usuario.objects.all()
        estudiantes_query = Estudiante.objects.all()
        profesores_query = Profesor.objects.all()
        suscripciones_query = Suscripcion.objects.all()
        pagos_query = Pago.objects.filter(estado='aprobado')
        
        # Aplicar filtros
        if fecha_inicio and fecha_fin:
            try:
                fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                suscripciones_query = suscripciones_query.filter(
                    fecha_inicio__gte=fecha_inicio_dt,
                    fecha_fin__lte=fecha_fin_dt
                )
                pagos_query = pagos_query.filter(
                    fecha__date__gte=fecha_inicio_dt,
                    fecha__date__lte=fecha_fin_dt
                )
            except ValueError:
                messages.error(request, 'Formato de fecha inválido')
        
        if filtro_colegio:
            estudiantes_query = estudiantes_query.filter(colegio_id=filtro_colegio)
            profesores_query = profesores_query.filter(colegio_id=filtro_colegio)
            suscripciones_query = suscripciones_query.filter(colegio_id=filtro_colegio)
        
        # ESTADÍSTICAS PRINCIPALES
        total_ingresos = pagos_query.aggregate(total=Sum('monto'))['total'] or 0
        
        estadisticas = {
            'total_colegios': colegios_query.count(),
            'total_usuarios': usuarios_query.count(),
            'total_estudiantes': estudiantes_query.count(),
            'total_profesores': profesores_query.count(),
            'total_suscripciones': suscripciones_query.count(),
            'ingresos_totales': float(total_ingresos),
        }
        
        # GRÁFICO DE TORTA - Distribución de usuarios por rol
        distribucion_roles = Usuario.objects.values('rol__tipo').annotate(
            total=Count('id')
        ).order_by('-total')
        
        datos_torta_roles = []
        for item in distribucion_roles:
            nombre_rol = item['rol__tipo'] if item['rol__tipo'] else 'Sin rol'
            datos_torta_roles.append({
                'name': nombre_rol, 
                'y': item['total']
            })
        
        # GRÁFICO DE BARRAS - Colegios con más estudiantes
        colegios_estudiantes = Colegio.objects.annotate(
            total_estudiantes=Count('estudiantes')
        ).order_by('-total_estudiantes')[:10]
        
        datos_barras_colegios = {
            'colegios': [colegio.nombre[:20] + '...' if len(colegio.nombre) > 20 else colegio.nombre 
                         for colegio in colegios_estudiantes],
            'estudiantes': [colegio.total_estudiantes for colegio in colegios_estudiantes]
        }
        
        # GRÁFICO DE BARRAS - Tipos de membresías
        membresias_suscripciones = Membresia.objects.annotate(
            total_suscripciones=Count('suscripciones')
        ).order_by('-total_suscripciones')
        
        datos_barras_membresias = {
            'membresias': [membresia.nombre for membresia in membresias_suscripciones],
            'suscripciones': [membresia.total_suscripciones for membresia in membresias_suscripciones]
        }
        
        # TABLA DE SUSCRIPCIONES RECIENTES
        suscripciones_recientes = suscripciones_query.select_related(
            'colegio', 'membresia'
        ).order_by('-fecha_inicio')[:10]
        
        # TABLA DE PAGOS RECIENTES
        pagos_recientes = pagos_query.select_related('usuario').order_by('-fecha')[:10]
        
        context = {
            'usuario': usuario,
            'estadisticas': estadisticas,
            'datos_torta_roles': json.dumps(datos_torta_roles),
            'datos_barras_colegios': json.dumps(datos_barras_colegios),
            'datos_barras_membresias': json.dumps(datos_barras_membresias),
            'suscripciones_recientes': suscripciones_recientes,
            'pagos_recientes': pagos_recientes,
            'colegios': colegios_query,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'filtro_colegio': filtro_colegio,
        }
        
        return render(request, 'superadministrador/dashboard_superadmin.html', context)
        
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('panel_admin')

# ====================================================================
# DASHBOARD ADMINISTRADOR 
# ====================================================================
@login_required_custom
def dashboard_administrador(request):
    usuario_id = request.session.get('usuario_id')

    try:
        usuario = Usuario.objects.get(id=usuario_id)
        
        # ===============================================================
        # VERIFICACIÓN DE ROL
        # ===============================================================
        if not usuario.rol:
            messages.error(request, 'Usuario sin rol asignado')
            return redirect('panel_admin')

        rol_tipo = usuario.rol.tipo.strip()

        # Solo administradores o superadministradores pueden acceder
        if rol_tipo not in ['Administrador', 'SuperAdmin']:
            messages.error(request, f'No tiene permisos para acceder al dashboard. Rol actual: {usuario.rol.tipo}')
            
            # Redirigir según su rol real
            if rol_tipo == 'Profesor':
                return redirect('dashboard_profesor')
            elif rol_tipo == 'Estudiante':
                return redirect('dashboard_estudiante')
            else:
                return redirect('login')

        # ===============================================================
        # PERFIL DE ADMINISTRADOR Y COLEGIO
        # ===============================================================
        administrador = Administrador.objects.filter(usuario=usuario).first()

        if administrador and administrador.colegio:
            colegio_admin = administrador.colegio
        else:
            colegio_admin = Colegio.objects.first()
            if not colegio_admin:
                messages.error(request, 'No hay colegios configurados en el sistema')
                context = {
                    'usuario': usuario,
                    'administrador': None,
                    'colegio': None,
                    'estadisticas': {},
                    'datos_torta_cursos': json.dumps([]),
                    'datos_barras_cursos': json.dumps({'cursos': [], 'estudiantes': []}),
                    'estudiantes_recientes': [],
                    'profesores': [],
                    'fecha_inicio': '',
                    'fecha_fin': '',
                }
                return render(request, 'administrador/dashboard_administrador.html', context)

        # ===============================================================
        # FILTROS
        # ===============================================================
        fecha_inicio = request.GET.get('fecha_inicio', '')
        fecha_fin = request.GET.get('fecha_fin', '')

        # ===============================================================
        # CONSULTAS BASE
        # ===============================================================
        estudiantes_query = Estudiante.objects.filter(colegio=colegio_admin)
        profesores_query = Profesor.objects.filter(colegio=colegio_admin)
        cursos_query = Curso.objects.filter(profesor__colegio=colegio_admin)

        suscripcion_query = Suscripcion.objects.filter(
            colegio=colegio_admin,
            fecha_fin__gte=timezone.now().date()
        ).first()

        # ===============================================================
        # ESTADÍSTICAS PRINCIPALES
        # ===============================================================
        try:
            dias_restantes = 0
            if suscripcion_query:
                dias_restantes = max(
                    (suscripcion_query.fecha_fin - timezone.now().date()).days, 0
                )
            
            estadisticas = {
                'total_estudiantes': estudiantes_query.count(),
                'total_profesores': profesores_query.count(),
                'total_cursos': cursos_query.count(),
                'membresia_actual': suscripcion_query.membresia.nombre if suscripcion_query else 'Sin membresía',
                'usuarios_actuales': suscripcion_query.usuarios_actuales if suscripcion_query else 0,
                'dias_restantes': dias_restantes,
            }
        except Exception as e:
            print(f"Error calculando estadísticas: {e}")
            estadisticas = {
                'total_estudiantes': 0,
                'total_profesores': 0,
                'total_cursos': 0,
                'membresia_actual': 'Error en datos',
                'usuarios_actuales': 0,
                'dias_restantes': 0,
            }

        # ===============================================================
        # GRÁFICO DE TORTA - Estudiantes por curso
        # ===============================================================
        try:
            estudiantes_por_curso = estudiantes_query.values('curso__nombre').annotate(
                total=Count('id')
            ).order_by('-total')

            datos_torta_cursos = [
                {'name': item['curso__nombre'] or 'Sin curso', 'y': item['total']}
                for item in estudiantes_por_curso
            ] or [{'name': 'No hay datos', 'y': 1}]
        except Exception as e:
            print(f"Error en gráfico de torta: {e}")
            datos_torta_cursos = [{'name': 'Error en datos', 'y': 1}]

        # ===============================================================
        # GRÁFICO DE BARRAS - Cursos con más estudiantes
        # ===============================================================
        try:
            cursos_con_estudiantes = estudiantes_query.values('curso__nombre').annotate(
                total=Count('id')
            ).order_by('-total')[:5]

            datos_barras_cursos = {
                'cursos': [c['curso__nombre'] or 'Sin curso' for c in cursos_con_estudiantes],
                'estudiantes': [c['total'] for c in cursos_con_estudiantes]
            }

            if not datos_barras_cursos['cursos']:
                datos_barras_cursos = {'cursos': ['No hay datos'], 'estudiantes': [0]}
        except Exception as e:
            print(f"Error en gráfico de barras: {e}")
            datos_barras_cursos = {'cursos': ['Error en datos'], 'estudiantes': [0]}

        # ===============================================================
        # TABLAS
        # ===============================================================
        try:
            estudiantes_recientes = estudiantes_query.select_related('persona', 'colegio').order_by('-id')[:10]
        except:
            estudiantes_recientes = []

        try:
            profesores_lista = profesores_query.select_related('usuario', 'colegio').order_by('usuario__correo')
        except:
            profesores_lista = []

        # ===============================================================
        # CONTEXTO FINAL
        # ===============================================================
        context = {
            'usuario': usuario,
            'administrador': administrador,
            'colegio': colegio_admin,
            'estadisticas': estadisticas,
            'datos_torta_cursos': json.dumps(datos_torta_cursos),
            'datos_barras_cursos': json.dumps(datos_barras_cursos),
            'estudiantes_recientes': estudiantes_recientes,
            'profesores': profesores_lista,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
        }

        return render(request, 'administrador/dashboard_administrador.html', context)

    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('login')
    except Exception as e:
        print(f"Error crítico en dashboard_administrador: {str(e)}")
        messages.error(request, f'Error al cargar el dashboard: {str(e)}')
        return redirect('panel_admin')


# ====================================================================
# DASHBOARD PROFESOR 
# ====================================================================
@login_required_custom
def dashboard_profesor(request):
    usuario_id = request.session.get('usuario_id')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        
        # Verificar que sea profesor
        if not usuario.rol:
            messages.error(request, 'Usuario sin rol asignado')
            return redirect('panel_profesor')
        
        if usuario.rol.tipo.strip() != 'Profesor':
            messages.error(request, 'No tiene permisos para acceder a esta página')
            return redirect('panel_profesor')
        
        # Obtener el profesor
        profesor = Profesor.objects.filter(usuario=usuario).first()
        
        if not profesor:
            # Si no tiene perfil de profesor, mostrar dashboard básico
            messages.warning(request, 'Perfil de profesor no encontrado, mostrando información básica')
            context = {
                'usuario': usuario,
                'profesor': None,
                'estadisticas': {
                    'total_cursos': 0,
                    'total_temas': 0,
                    'temas_disponibles': 0,
                    'temas_no_disponibles': 0,
                },
                'datos_torta_temas': json.dumps([]),
                'datos_barras_temas': json.dumps({'cursos': [], 'temas': []}),
                'temas_recientes': [],
                'cursos': [],
                'fecha_inicio': '',
                'fecha_fin': '',
                'curso_filtro': '',
            }
            return render(request, 'profesor/dashboard_profesor.html', context)
        
        # FILTROS
        fecha_inicio = request.GET.get('fecha_inicio', '')
        fecha_fin = request.GET.get('fecha_fin', '')
        curso_filtro = request.GET.get('curso', '')
        
        # Consultas base del profesor CON ANNOTATE
        cursos_query = Curso.objects.filter(profesor=profesor).annotate(total_temas=Count('temas'))
        temas_query = Temas.objects.filter(curso__profesor=profesor)
        
        if curso_filtro:
            cursos_query = cursos_query.filter(id=curso_filtro)
            temas_query = temas_query.filter(curso_id=curso_filtro)
        
        # Aplicar filtros de fecha si existen
        if fecha_inicio and fecha_fin:
            try:
                fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                temas_query = temas_query.filter(
                    fecha_inicio__gte=fecha_inicio_dt,
                    fecha_inicio__lte=fecha_fin_dt
                )
            except ValueError:
                messages.error(request, 'Formato de fecha inválido')
        
        # ESTADÍSTICAS PRINCIPALES
        estadisticas = {
            'total_cursos': cursos_query.count(),
            'total_temas': temas_query.count(),
            'temas_disponibles': temas_query.filter(estado='disponible').count(),
            'temas_no_disponibles': temas_query.filter(estado='no disponible').count(),
        }
        
        # GRÁFICO DE TORTA - Estado de temas
        datos_torta_temas = [
            {'name': 'Disponibles', 'y': estadisticas['temas_disponibles']},
            {'name': 'No Disponibles', 'y': estadisticas['temas_no_disponibles']},
        ]
        
        # GRÁFICO DE BARRAS - Temas por curso
        datos_barras_temas = {
            'cursos': [curso.nombre for curso in cursos_query],
            'temas': [curso.total_temas for curso in cursos_query]
        }
        
        # TABLA DE TEMAS RECIENTES
        temas_recientes = temas_query.select_related('curso').order_by('-fecha_inicio')[:10]
        
        # TABLA DE CURSOS
        cursos_lista = cursos_query.order_by('nombre')
        
        context = {
            'usuario': usuario,
            'profesor': profesor,
            'estadisticas': estadisticas,
            'datos_torta_temas': json.dumps(datos_torta_temas),
            'datos_barras_temas': json.dumps(datos_barras_temas),
            'temas_recientes': temas_recientes,
            'cursos': cursos_lista,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'curso_filtro': curso_filtro,
        }
        
        return render(request, 'profesor/dashboard_profesor.html', context)
        
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('panel_profesor') 
        
# ====================================================================
# DASHBOARD ESTUDIANTE
# ====================================================================
@login_required_custom
def dashboard_estudiante(request):
    usuario_id = request.session.get('usuario_id')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)

        # Verificar que el usuario tenga rol
        if not usuario.rol or not usuario.rol.tipo:
            messages.error(request, 'Usuario sin rol asignado')
            return redirect('login')

        # Normalizar el tipo de rol
        rol_tipo = usuario.rol.tipo.strip()

        # Verificar que sea estudiante
        if rol_tipo != 'Estudiante':
            messages.error(request, f'Acceso denegado: su rol es "{usuario.rol.tipo}".')
            return redirect('login')

        # Obtener el perfil de persona
        persona = usuario.personas.first()
        if not persona:
            messages.error(request, 'Perfil de persona no encontrado')
            return redirect('panel_estudiante')
            
        # Obtener el estudiante asociado
        estudiante = Estudiante.objects.filter(persona=persona).first()
        if not estudiante:
            messages.error(request, 'Perfil de estudiante no encontrado')
            return redirect('panel_estudiante')
        
        # Consultas del estudiante
        temas_query = Temas.objects.filter(
            curso=estudiante.curso,
            estado='disponible'
        )
        
        laboratorios_query = Laboratorio.objects.filter(
            curso=estudiante.curso,
            estado='activo'
        )
        
        # ESTADÍSTICAS PRINCIPALES
        estadisticas = {
            'total_temas_disponibles': temas_query.count(),
            'total_laboratorios': laboratorios_query.count(),
            'curso_actual': estudiante.curso.nombre if estudiante.curso else 'Sin curso asignado',
            'colegio': estudiante.colegio.nombre if estudiante.colegio else 'Sin colegio',
        }
        
        # GRÁFICO DE TORTA - Temas disponibles (ejemplo)
        datos_torta_progreso = [
            {'name': 'Temas Disponibles', 'y': estadisticas['total_temas_disponibles']},
            {'name': 'Laboratorios Activos', 'y': estadisticas['total_laboratorios']},
        ]
        
        # TABLAS
        temas_disponibles = temas_query.select_related('curso').order_by('numero')[:10]
        laboratorios_activos = laboratorios_query.order_by('nombre')[:10]
        
        context = {
            'usuario': usuario,
            'estudiante': estudiante,
            'estadisticas': estadisticas,
            'datos_torta_progreso': json.dumps(datos_torta_progreso),
            'temas_disponibles': temas_disponibles,
            'laboratorios_activos': laboratorios_activos,
        }
        
        return render(request, 'estudiante/dashboard_estudiante.html', context)
        
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('login')
        
    except Exception as e:
        print(f"Error en dashboard_estudiante: {str(e)}")
        messages.error(request, f'Ocurrió un error: {str(e)}')
        return redirect('panel_estudiante')

# ====================================================================
# GENERAR REPORTES PDF
# ====================================================================
@login_required_custom
def generar_reporte_pdf(request, tipo_reporte):
    usuario_id = request.session.get('usuario_id')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        rol = usuario.rol.tipo.strip() if usuario.rol else ''
        
        # Crear el response PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Título del reporte
        titulo = f"Reporte - {tipo_reporte.replace('_', ' ').title()}"
        elements.append(Paragraph(titulo, styles['Title']))
        elements.append(Paragraph(f"Generado por: {usuario.correo}", styles['Normal']))
        elements.append(Paragraph(f"Fecha: {timezone.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # CONTENIDO DEL REPORTE SEGÚN ROL Y TIPO
        if rol == 'SuperAdmin':
            data = generar_reporte_superadmin(tipo_reporte, usuario)
        elif rol == 'Administrador':
            data = generar_reporte_administrador(tipo_reporte, usuario)
        elif rol == 'Profesor':
            data = generar_reporte_profesor(tipo_reporte, usuario)
        elif rol == 'Estudiante':
            data = generar_reporte_estudiante(tipo_reporte, usuario)
        else:
            data = [['No hay datos disponibles para este rol']]
        
        # Crear tabla
        if data and len(data) > 1:  # Si hay datos además del encabezado
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("No hay datos disponibles para este reporte.", styles['Normal']))
        
        # Generar PDF
        doc.build(elements)
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_{tipo_reporte}_{timezone.now().strftime("%Y%m%d_%H%M")}.pdf"'
        
        return response
        
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'Error al generar el reporte: {str(e)}')
        return redirect('panel_admin')

# ====================================================================
# FUNCIONES AUXILIARES PARA REPORTES
# ====================================================================
def generar_reporte_superadmin(tipo_reporte, usuario):
    """Genera datos para reportes del superadministrador"""
    if tipo_reporte == 'usuarios':
        usuarios = Usuario.objects.select_related('rol').values_list(
            'correo', 'rol__tipo', 'estado'
        )
        data = [['Correo', 'Rol', 'Estado']]
        data.extend(list(usuarios))
        
    elif tipo_reporte == 'colegios':
        colegios = Colegio.objects.all().values_list('nombre', 'direccion')
        data = [['Nombre', 'Dirección']]
        data.extend(list(colegios))
        
    elif tipo_reporte == 'suscripciones':
        suscripciones = Suscripcion.objects.select_related('colegio', 'membresia').values_list(
            'colegio__nombre', 'membresia__nombre', 'fecha_inicio', 'fecha_fin', 'usuarios_actuales'
        )
        data = [['Colegio', 'Membresía', 'Fecha Inicio', 'Fecha Fin', 'Usuarios Actuales']]
        data.extend(list(suscripciones))
        
    elif tipo_reporte == 'pagos':
        pagos = Pago.objects.select_related('usuario').filter(estado='aprobado').values_list(
            'usuario__correo', 'monto', 'fecha', 'metodo'
        )
        data = [['Usuario', 'Monto', 'Fecha', 'Método']]
        data.extend(list(pagos))
        
    else:
        data = [['Reporte no disponible']]
    
    return data

def generar_reporte_administrador(tipo_reporte, usuario):
    """Genera datos para reportes del administrador"""
    # Obtener el colegio del administrador (en implementación real)
    colegio_admin = Colegio.objects.first()
    
    if tipo_reporte == 'estudiantes':
        estudiantes = Estudiante.objects.filter(colegio=colegio_admin).select_related('persona').values_list(
            'persona__nombre', 'persona__apellidoPaterno', 'persona__apellidoMaterno', 'curso'
        )
        data = [['Nombre', 'Apellido Paterno', 'Apellido Materno', 'Curso']]
        data.extend(list(estudiantes))
        
    elif tipo_reporte == 'profesores':
        profesores = Profesor.objects.filter(colegio=colegio_admin).select_related('usuario').values_list(
            'usuario__correo', 'curso'
        )
        data = [['Correo', 'Curso']]
        data.extend(list(profesores))
        
    elif tipo_reporte == 'cursos':
        cursos = Curso.objects.filter(profesor__colegio=colegio_admin).values_list(
            'nombre', 'profesor__usuario__correo'
        )
        data = [['Curso', 'Profesor']]
        data.extend(list(cursos))
        
    else:
        data = [['Reporte no disponible']]
    
    return data

def generar_reporte_profesor(tipo_reporte, usuario):
    """Genera datos para reportes del profesor"""
    profesor = Profesor.objects.filter(usuario=usuario).first()
    
    if not profesor:
        return [['Profesor no encontrado']]
    
    if tipo_reporte == 'cursos':
        cursos = Curso.objects.filter(profesor=profesor).values_list('nombre', 'id')
        data = [['Nombre del Curso', 'ID']]
        data.extend(list(cursos))
        
    elif tipo_reporte == 'temas':
        temas = Temas.objects.filter(curso__profesor=profesor).select_related('curso').values_list(
            'nombre_archivo', 'curso__nombre', 'estado', 'fecha_inicio', 'numero'
        )
        data = [['Tema', 'Curso', 'Estado', 'Fecha Inicio', 'Número']]
        data.extend(list(temas))
        
    else:
        data = [['Reporte no disponible']]
    
    return data

def generar_reporte_estudiante(tipo_reporte, usuario):
    """Genera datos para reportes del estudiante"""
    persona = usuario.personas.first()
    estudiante = Estudiante.objects.filter(persona=persona).first()
    
    if not estudiante:
        return [['Estudiante no encontrado']]
    
    if tipo_reporte == 'temas_disponibles':
        temas = Temas.objects.filter(
            curso__profesor__colegio=estudiante.colegio,
            estado='disponible'
        ).select_related('curso').values_list('nombre_archivo', 'curso__nombre', 'fecha_inicio', 'numero')
        data = [['Tema', 'Curso', 'Fecha Inicio', 'Número']]
        data.extend(list(temas))
        
    elif tipo_reporte == 'laboratorios':
        laboratorios = Laboratorio.objects.filter(estado='activo').values_list(
            'nombre', 'estado'
        )
        data = [['Laboratorio', 'Estado']]
        data.extend(list(laboratorios))
        
    else:
        data = [['Reporte no disponible']]
    
    return data

# ====================================================================
# APIS PARA DATOS EN TIEMPO REAL (AJAX)
# ====================================================================
@login_required_custom
def api_estadisticas_tiempo_real(request):
    """API para obtener estadísticas en tiempo real"""
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return JsonResponse({'error': 'No autenticado'}, status=401)
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        rol = usuario.rol.tipo.strip() if usuario.rol else ''
        
        data = {}
        hoy = timezone.now().date()
        
        if rol == 'SuperAdmin':
            # Estadísticas en tiempo real para superadmin
            data = {
                'total_usuarios': Usuario.objects.count(),
                'total_colegios': Colegio.objects.count(),
                'ingresos_hoy': float(Pago.objects.filter(
                    fecha__date=hoy, 
                    estado='aprobado'
                ).aggregate(Sum('monto'))['monto__sum'] or 0),
                'suscripciones_activas': Suscripcion.objects.filter(
                    fecha_fin__gte=hoy
                ).count(),
            }
            
        elif rol == 'Administrador':
            # Estadísticas para administrador
            colegio_admin = Colegio.objects.first()  # En realidad vendría de la relación
            data = {
                'estudiantes_totales': Estudiante.objects.filter(colegio=colegio_admin).count(),
                'profesores_totales': Profesor.objects.filter(colegio=colegio_admin).count(),
                'cursos_totales': Curso.objects.filter(profesor__colegio=colegio_admin).count(),
            }
            
        elif rol == 'Profesor':
            # Estadísticas para profesor
            profesor = Profesor.objects.filter(usuario=usuario).first()
            if profesor:
                data = {
                    'cursos_totales': Curso.objects.filter(profesor=profesor).count(),
                    'temas_totales': Temas.objects.filter(curso__profesor=profesor).count(),
                    'temas_disponibles': Temas.objects.filter(
                        curso__profesor=profesor, 
                        estado='disponible'
                    ).count(),
                }
                
        elif rol == 'Estudiante':
            # Estadísticas para estudiante
            persona = usuario.personas.first()
            estudiante = Estudiante.objects.filter(persona=persona).first()
            if estudiante:
                data = {
                    'temas_disponibles': Temas.objects.filter(
                        curso__profesor__colegio=estudiante.colegio,
                        estado='disponible'
                    ).count(),
                    'laboratorios_activos': Laboratorio.objects.filter(estado='activo').count(),
                }
        
        return JsonResponse({'success': True, 'data': data})
        
    except Usuario.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ====================================================================
# VISTA PRINCIPAL DE INFORMES
# ====================================================================
@login_required_custom
def informes_principal(request):
    """Vista principal que redirige al dashboard según el rol"""
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        rol = usuario.rol.tipo.strip() if usuario.rol else ''
        
        if rol == 'SuperAdmin':
            return redirect('dashboard_superadmin')
        elif rol == 'Administrador':
            return redirect('dashboard_administrador')
        elif rol == 'Profesor':
            return redirect('dashboard_profesor')
        elif rol == 'Estudiante':
            return redirect('dashboard_estudiante')
        else:
            messages.error(request, 'Rol no reconocido')
            return redirect('panel_admin')
            
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('login')

##VISTA PARA CONTENIDO TEORICO##

def gestion_documentos(request):
    """
    Vista exclusiva para administradores para gestionar documentos
    """
    documentos = Documento.objects.all().order_by('-fecha_creacion')
    
    if request.method == 'POST':
        # Manejar AJAX requests para crear/editar/eliminar
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return manejar_ajax_documentos(request)
    
    return render(request, 'profesor/gestion_documentos.html', {
        'documentos': documentos
    })
    
def crear_documento_ajax(request):
    """Crear documento via AJAX con archivo PDF"""
    try:
        nombre = request.POST.get('nombre', '').strip()
        if not nombre:
            return JsonResponse({'error': 'El nombre es requerido'}, status=400)
        
        # Crear documento
        documento = Documento(
            nombre=nombre,
            descripcion=request.POST.get('descripcion', ''),
            estado=request.POST.get('estado', 'Activo'),
            categoria='fisica_general'
        )
        
        # Manejar archivo PDF si se subió
        if 'archivo_pdf' in request.FILES:
            archivo = request.FILES['archivo_pdf']
            documento.archivo_pdf = archivo.read()  # Guardar binario
            documento.nombre_archivo = archivo.name
            documento.tamaño = archivo.size
        
        documento.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Documento creado correctamente' + (' con PDF' if 'archivo_pdf' in request.FILES else '')
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def manejar_ajax_documentos(request):
    """Manejar operaciones AJAX para documentos"""
    if request.method == 'POST':
        try:
            # Verificar si es FormData (con archivos)
            if request.content_type.startswith('multipart/form-data'):
                action = request.POST.get('action', 'crear')
                
                if action == 'crear':
                    return crear_documento_ajax(request)
                # ... otras acciones
            else:
                # Manejo normal JSON
                data = json.loads(request.body)
                action = data.get('action')
                
                if action == 'crear':
                    return crear_documento_ajax(data)
                elif action == 'editar':
                    return editar_documento_ajax(data)
                elif action == 'eliminar':
                    return eliminar_documento_ajax(data)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

    
def editar_documento_ajax(data):
    """Editar documento via AJAX"""
    try:
        documento_id = data.get('id')
        if not documento_id:
            return JsonResponse({'error': 'ID de documento requerido'}, status=400)
        
        documento = Documento.objects.get(id=documento_id)
        documento.nombre = data.get('nombre', documento.nombre).strip()
        documento.descripcion = data.get('descripcion', documento.descripcion)
        documento.estado = data.get('estado', documento.estado)
        documento.categoria = data.get('categoria', documento.categoria)
        documento.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Documento actualizado correctamente'
        })
        
    except Documento.DoesNotExist:
        return JsonResponse({'error': 'Documento no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def eliminar_documento_ajax(data):
    """Eliminar documento via AJAX"""
    try:
        documento_id = data.get('id')
        if not documento_id:
            return JsonResponse({'error': 'ID de documento requerido'}, status=400)
        
        documento = Documento.objects.get(id=documento_id)
        documento_nombre = documento.nombre
        documento.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Documento "{documento_nombre}" eliminado correctamente'
        })
        
    except Documento.DoesNotExist:
        return JsonResponse({'error': 'Documento no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def contenido_teorico(request):
    """Vista para mostrar el contenido teórico a los usuarios"""
    # Obtener todos los documentos activos
    documentos = Documento.objects.filter(estado='Activo').order_by('categoria', 'nombre')
    
    # Agrupar por categoría y preparar datos para el template
    categorias = {}
    for doc in documentos:
        if doc.categoria not in categorias:
            categorias[doc.categoria] = []
        
        # Crear un diccionario con toda la información necesaria
        doc_data = {
            'id': doc.id,
            'nombre': doc.nombre,
            'descripcion': doc.descripcion,
            'nombre_archivo': doc.nombre_archivo,
            'tamaño': doc.tamaño,
            'fecha_actualizacion': doc.fecha_actualizacion,
            'get_tamaño_formateado': doc.get_tamaño_formateado(),
        }
        categorias[doc.categoria].append(doc_data)
    
    # Si hay búsqueda, filtrar resultados
    query = request.GET.get('q', '')
    if query:
        documentos_filtrados = documentos.filter(
            Q(nombre__icontains=query) | 
            Q(descripcion__icontains=query) |
            Q(categoria__icontains=query)
        )
        
        categorias_filtradas = {}
        for doc in documentos_filtrados:
            if doc.categoria not in categorias_filtradas:
                categorias_filtradas[doc.categoria] = []
            
            doc_data = {
                'id': doc.id,
                'nombre': doc.nombre,
                'descripcion': doc.descripcion,
                'nombre_archivo': doc.nombre_archivo,
                'tamaño': doc.tamaño,
                'fecha_actualizacion': doc.fecha_actualizacion,
                'get_tamaño_formateado': doc.get_tamaño_formateado(),
            }
            categorias_filtradas[doc.categoria].append(doc_data)
        
        categorias = categorias_filtradas
    
    context = {
        'categorias': categorias,
        'query': query
    }
    return render(request, 'estudiante/contenido_temas.html', context)

def descargar_documento(request, documento_id):
    """Vista para descargar documentos PDF"""
    try:
        documento = get_object_or_404(Documento, id=documento_id, estado='Activo')
        
        # Verificar que el documento tenga archivo PDF
        if not documento.archivo_pdf:
            return HttpResponse('El documento no tiene archivo PDF', status=404)
        
        # Crear respuesta con el PDF
        response = HttpResponse(documento.archivo_pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{documento.nombre_archivo or documento.nombre}.pdf"'
        return response
        
    except Exception as e:
        return HttpResponse(f'Error al descargar el documento: {str(e)}', status=500)

def preview_documento(request, documento_id):
    """Vista para previsualizar documentos PDF"""
    try:
        documento = get_object_or_404(Documento, id=documento_id, estado='Activo')
        
        # Verificar que el documento tenga archivo PDF
        if not documento.archivo_pdf:
            return HttpResponse('El documento no tiene archivo PDF', status=404)
        
        # Crear respuesta para visualización en línea
        response = HttpResponse(documento.archivo_pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{documento.nombre_archivo or documento.nombre}.pdf"'
        return response
        
    except Exception as e:
        return HttpResponse(f'Error al visualizar el documento: {str(e)}', status=500)

# =====================
# COMPONENTES EN TARJETAS PARA PROFESOR
# =====================
from django.core.serializers.json import DjangoJSONEncoder

def componentes_profesor_tarjetas(request):
    componentes = Componente.objects.all().select_related('tema', 'laboratorio')
    # Serializar componentes para JS
    componentes_json = []
    for c in componentes:
        componentes_json.append({
            'id': c.id,
            'nombre': c.nombre,
            'descripcion': c.descripcion,
            'especificaciones': c.especificaciones,
            'imagen_url': c.imagen.url if c.imagen else '',
            'modelo3D_url': c.modelo3D.url if c.modelo3D else '',
            'video_explicacion': c.video_explicacion,
            'tema_nombre': c.tema.nombre_archivo if c.tema else '',
            'laboratorio_nombre': c.laboratorio.nombre if c.laboratorio else '',
        })
    context = {
        'componentes': componentes,
        'componentes_json': json.dumps(componentes_json, cls=DjangoJSONEncoder)
    }
    return render(request, 'profesor/componentes_tarjetas.html', context)

# =====================
# COMPONENTES EN TARJETAS PARA ESTUDIANTE
# =====================
def componentes_estudiante_tarjetas(request):
    componentes = Componente.objects.all().select_related('tema', 'laboratorio')
    componentes_json = []
    for c in componentes:
        componentes_json.append({
            'id': c.id,
            'nombre': c.nombre,
            'descripcion': c.descripcion,
            'especificaciones': c.especificaciones,
            'imagen_url': c.imagen.url if c.imagen else '',
            'modelo3D_url': c.modelo3D.url if c.modelo3D else '',
            'video_explicacion': c.video_explicacion,
            'tema_nombre': c.tema.nombre_archivo if c.tema else '',
            'laboratorio_nombre': c.laboratorio.nombre if c.laboratorio else '',
        })
    context = {
        'componentes': componentes,
        'componentes_json': json.dumps(componentes_json, cls=DjangoJSONEncoder)
    }
    return render(request, 'estudiante/componentes_tarjetas.html', context)