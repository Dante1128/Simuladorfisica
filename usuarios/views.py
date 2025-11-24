# ======================
# IMPORTS DE DJANGO
# ======================
from django.shortcuts import render
from .models import ConfiguracionVisual
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
from django.template.loader import render_to_string
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Sum
from django.db import models
from django.contrib.admin.views.decorators import staff_member_required
from .models import Colegio, ConfiguracionVisual

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
                return redirect('panel_superadmin')
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
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        
        context = {
            'usuario': usuario,
            'total_colegios': Colegio.objects.count(),
            'total_usuarios': Usuario.objects.count(),
            'total_estudiantes': Estudiante.objects.count(),
            'total_profesores': Profesor.objects.count(),
            'total_cursos': Curso.objects.count(),
            'total_laboratorios': Laboratorio.objects.count(),
            
        
        }
        
        return render(request, 'superadministrador/panel_superadmin.html', context)
        
    except Usuario.DoesNotExist:
        return redirect('login')

def base_superadmin(request):
    """Vista básica para base de administración"""
    return render(request, 'superadministrador/base_superadmin.html')

def perfil_superadmin(request):
    """Vista básica para perfil de administración"""
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        return render(request, 'superadministrador/perfil_superadmin.html', {"usuario": usuario})
    except Usuario.DoesNotExist:
        return redirect('login')

def gestion_colegios(request):
    # =========================
    # CAMBIO DE ESTADO
    # =========================
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

    # =========================
    # CREAR COLEGIO + CONFIGURACION VISUAL
    # =========================
    if request.method == 'POST' and 'crear' in request.POST:
        nombre = request.POST.get('nombre', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        color_primario = request.POST.get('color_primario', '#007bff')
        color_secundario = request.POST.get('color_secundario', '#6c757d')
        logo = request.FILES.get('logo')
      
        if nombre and direccion:
            if not Colegio.objects.filter(nombre__iexact=nombre).exists():
                colegio = Colegio.objects.create(nombre=nombre, direccion=direccion)
                # Crear configuración visual
                ConfiguracionVisual.objects.create(
                    colegio=colegio,
                    color_primario=color_primario,
                    color_secundario=color_secundario,
                    logo=logo,
                )
                messages.success(request, 'Colegio creado correctamente con configuración visual.')
            else:
                messages.error(request, 'Ya existe un colegio con ese nombre.')
        else:
            messages.error(request, 'Todos los campos son obligatorios.')

    # =========================
    # EDITAR COLEGIO
    # =========================
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

    # =========================
    # FILTRO
    # =========================
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
    # CREAR ESTUDIANTE
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
                rol_estudiante = Rol.objects.get(id=4)  # ID 4 para estudiantes
                usuario = Usuario.objects.create(
                    correo=correo,
                    contrasenia=make_password(contrasenia),
                    estado='Activo',
                    rol=rol_estudiante
                )
                from .models import Persona
                persona = Persona.objects.create(
                    usuario=usuario,
                    nombre=nombre,
                    apellidoPaterno=apellidoPaterno,
                    apellidoMaterno=apellidoMaterno
                )
                # 👇 aquí el cambio: usar estado, no activo
                estudiante = Estudiante.objects.create(
                    persona=persona,
                    colegio_id=colegio_id,
                    curso=curso,
                    estado='Activo'  # Estado inicial
                )
                messages.success(request, 'Estudiante creado correctamente.')
                return redirect('gestion_estudiante')
            else:
                messages.error(request, 'Ya existe un usuario con ese correo.')
        else:
            messages.error(request, 'Todos los campos son obligatorios.')

    # EDITAR ESTUDIANTE
    if request.method == 'POST' and 'editar_id' in request.POST:
        editar_id = request.POST.get('editar_id')
        nombre = request.POST.get('editar_nombre', '').strip()
        apellidoPaterno = request.POST.get('editar_apellidoPaterno', '').strip()
        apellidoMaterno = request.POST.get('editar_apellidoMaterno', '').strip()
        correo = request.POST.get('editar_correo', '').strip()
        contrasenia = request.POST.get('editar_contrasenia', '').strip()
        colegio_id = request.POST.get('editar_colegio')
        curso = request.POST.get('editar_curso', '').strip()
        
        estudiante = Estudiante.objects.filter(id=editar_id).first()
        if estudiante and nombre and apellidoPaterno and apellidoMaterno and correo and colegio_id and curso:
            usuario = estudiante.persona.usuario
            if not Usuario.objects.filter(correo=correo).exclude(id=usuario.id).exists():
                usuario.correo = correo
                if contrasenia:
                    usuario.contrasenia = make_password(contrasenia)
                usuario.save()
                
                persona = estudiante.persona
                persona.nombre = nombre
                persona.apellidoPaterno = apellidoPaterno
                persona.apellidoMaterno = apellidoMaterno
                persona.save()
                
                estudiante.colegio_id = colegio_id
                estudiante.curso = curso
                estudiante.save()
                
                messages.success(request, 'Estudiante editado correctamente.')
                return redirect('gestion_estudiante')
            else:
                messages.error(request, 'Ya existe un usuario con ese correo.')
        else:
            messages.error(request, 'Todos los campos son obligatorios para editar.')

    # CAMBIAR ESTADO DEL ESTUDIANTE
    if request.method == "POST" and request.POST.get('cambiar_estado') == '1':
        estudiante_id = request.POST.get('estudiante_id')
        estudiante = Estudiante.objects.filter(id=estudiante_id).first()
        if estudiante:
            # 👇 Cambiamos entre 'Activo' e 'Inactivo'
            estudiante.estado = 'Inactivo' if estudiante.estado == 'Activo' else 'Activo'
            estudiante.save()
            messages.success(request, f"Estado del estudiante cambiado a {estudiante.estado}.")
        else:
            messages.error(request, 'Estudiante no encontrado.')
        return redirect('gestion_estudiante')

    # LISTAR ESTUDIANTES
    estudiantes = Estudiante.objects.select_related('persona', 'persona__usuario', 'colegio').all().order_by('persona__usuario__correo')
    colegios = Colegio.objects.all().order_by('nombre')
    
    context = {
        'estudiantes': estudiantes,
        'colegios': colegios,
    }
    return render(request, 'superadministrador/gestion_estudiante.html', context)

# =================================================================
# ADMINISTRADOR 
# =================================================================
def panel_admin(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        return render(request, 'administrador/panel_admin.html', {"usuario": usuario})
    except Usuario.DoesNotExist:
        return redirect('login')

def base_admin(request):
    return render(request, 'administrador/base_admin.html')

def perfil_admin(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        return render(request, 'administrador/perfil_admin.html', {"usuario": usuario})
    except Usuario.DoesNotExist:
        return redirect('login')
    
def gestion_adminprofesor(request):
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
        return redirect('gestion_adminprofesor')

    # LISTAR PROFESORES
    profesores = Profesor.objects.select_related('usuario', 'colegio').all().order_by('usuario__correo')
    colegios = Colegio.objects.all().order_by('nombre')
    context = {
        'profesores': profesores,
        'colegios': colegios,
    }
    return render(request, 'administrador/gestion_adminprofesor.html', context)


def gestion_adminestudiante(request):
    # CREAR ESTUDIANTE
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
                rol_estudiante = Rol.objects.get(id=4)  # ID 4 para estudiantes
                usuario = Usuario.objects.create(
                    correo=correo,
                    contrasenia=make_password(contrasenia),
                    estado='Activo',
                    rol=rol_estudiante
                )
                from .models import Persona
                persona = Persona.objects.create(
                    usuario=usuario,
                    nombre=nombre,
                    apellidoPaterno=apellidoPaterno,
                    apellidoMaterno=apellidoMaterno
                )
                # 👇 aquí el cambio: usar estado, no activo
                estudiante = Estudiante.objects.create(
                    persona=persona,
                    colegio_id=colegio_id,
                    curso=curso,
                    estado='Activo'  # Estado inicial
                )
                messages.success(request, 'Estudiante creado correctamente.')
                return redirect('gestion_adminestudiante')
            else:
                messages.error(request, 'Ya existe un usuario con ese correo.')
        else:
            messages.error(request, 'Todos los campos son obligatorios.')

    # EDITAR ESTUDIANTE
    if request.method == 'POST' and 'editar_id' in request.POST:
        editar_id = request.POST.get('editar_id')
        nombre = request.POST.get('editar_nombre', '').strip()
        apellidoPaterno = request.POST.get('editar_apellidoPaterno', '').strip()
        apellidoMaterno = request.POST.get('editar_apellidoMaterno', '').strip()
        correo = request.POST.get('editar_correo', '').strip()
        contrasenia = request.POST.get('editar_contrasenia', '').strip()
        colegio_id = request.POST.get('editar_colegio')
        curso = request.POST.get('editar_curso', '').strip()
        
        estudiante = Estudiante.objects.filter(id=editar_id).first()
        if estudiante and nombre and apellidoPaterno and apellidoMaterno and correo and colegio_id and curso:
            usuario = estudiante.persona.usuario
            if not Usuario.objects.filter(correo=correo).exclude(id=usuario.id).exists():
                usuario.correo = correo
                if contrasenia:
                    usuario.contrasenia = make_password(contrasenia)
                usuario.save()
                
                persona = estudiante.persona
                persona.nombre = nombre
                persona.apellidoPaterno = apellidoPaterno
                persona.apellidoMaterno = apellidoMaterno
                persona.save()
                
                estudiante.colegio_id = colegio_id
                estudiante.curso = curso
                estudiante.save()
                
                messages.success(request, 'Estudiante editado correctamente.')
                return redirect('gestion_adminestudiante')
            else:
                messages.error(request, 'Ya existe un usuario con ese correo.')
        else:
            messages.error(request, 'Todos los campos son obligatorios para editar.')

    # CAMBIAR ESTADO DEL ESTUDIANTE
    if request.method == "POST" and request.POST.get('cambiar_estado') == '1':
        estudiante_id = request.POST.get('estudiante_id')
        estudiante = Estudiante.objects.filter(id=estudiante_id).first()
        if estudiante:
            # 👇 Cambiamos entre 'Activo' e 'Inactivo'
            estudiante.estado = 'Inactivo' if estudiante.estado == 'Activo' else 'Activo'
            estudiante.save()
            messages.success(request, f"Estado del estudiante cambiado a {estudiante.estado}.")
        else:
            messages.error(request, 'Estudiante no encontrado.')
        return redirect('gestion_adminestudiante')

    # LISTAR ESTUDIANTES
    estudiantes = Estudiante.objects.select_related('persona', 'persona__usuario', 'colegio').all().order_by('persona__usuario__correo')
    colegios = Colegio.objects.all().order_by('nombre')
    
    context = {
        'estudiantes': estudiantes,
        'colegios': colegios,
    }
    return render(request, 'administrador/gestion_adminestudiante.html', context)

def gestion_admincurso(request):
    # CREAR CURSO
    if request.method == 'POST' and 'crear' in request.POST:
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        colegio_id = request.POST.get('colegio')
        profesor_id = request.POST.get('profesor', '').strip()

        if nombre and colegio_id:
            # Evitar duplicados
            if not Curso.objects.filter(nombre=nombre, colegio_id=colegio_id).exists():
                Curso.objects.create(
                    nombre=nombre,
                    descripcion=descripcion or None,
                    colegio_id=colegio_id,
                    profesor_id=profesor_id or None,
                    estado='Activo'
                )
                messages.success(request, '✅ Curso creado correctamente.')
            else:
                messages.error(request, '⚠️ Ya existe un curso con ese nombre en este colegio.')
        else:
            messages.error(request, '❌ Nombre y colegio son campos obligatorios.')
        return redirect('gestion_admincursos')

    # EDITAR CURSO
    elif request.method == 'POST' and 'editar_id' in request.POST:
        editar_id = request.POST.get('editar_id')
        nombre = request.POST.get('editar_nombre', '').strip()
        descripcion = request.POST.get('editar_descripcion', '').strip()
        colegio_id = request.POST.get('editar_colegio')
        profesor_id = request.POST.get('editar_profesor', '').strip()

        curso = Curso.objects.filter(id=editar_id).first()
        if curso and nombre and colegio_id:
            # Evitar duplicados en edición
            if not Curso.objects.filter(nombre=nombre, colegio_id=colegio_id).exclude(id=editar_id).exists():
                curso.nombre = nombre
                curso.descripcion = descripcion or None
                curso.colegio_id = colegio_id
                curso.profesor_id = profesor_id or None
                curso.save()
                messages.success(request, '✅ Curso actualizado correctamente.')
            else:
                messages.error(request, '⚠️ Ya existe otro curso con ese nombre en este colegio.')
        else:
            messages.error(request, '❌ Nombre y colegio son campos obligatorios para editar.')
        return redirect('gestion_admincursos')

    # CAMBIAR ESTADO DEL CURSO
    elif request.method == "POST" and request.POST.get('cambiar_estado') == '1':
        curso_id = request.POST.get('curso_id')
        curso = Curso.objects.filter(id=curso_id).first()
        if curso:
            curso.estado = 'Inactivo' if curso.estado == 'Activo' else 'Activo'
            curso.save()
            messages.success(request, f"✅ Estado del curso cambiado a {curso.estado}.")
        else:
            messages.error(request, '❌ Curso no encontrado.')
        return redirect('gestion_admincursos')

    # LISTAR CURSOS con información del profesor y cantidad de estudiantes
    cursos = Curso.objects.select_related(
        'colegio',
        'profesor',
        'profesor__persona'
    ).prefetch_related('estudiante_set').all().order_by('nombre')

    # Contar estudiantes por curso
    for curso in cursos:
        curso.estudiantes_count = curso.estudiante_set.count()

    colegios = Colegio.objects.all().order_by('nombre')
    profesores = Profesor.objects.select_related('persona', 'colegio').filter(estado='Activo').order_by('persona__nombre')

    context = {
        'cursos': cursos,
        'colegios': colegios,
        'profesores': profesores,
    }
    return render(request, 'administrador/gestion_admincurso.html', context)
# =================================================================
# PROFESOR
# =================================================================
def panel_profesor(request):

    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        return render(request, 'profesor/panel_profesor.html', {"usuario": usuario})
    except Usuario.DoesNotExist:
        return redirect('login')

def base_profesor(request):
    """Vista básica para base de administración"""
    return render(request, 'profesor/base_profesor.html')

def perfil_profesor(request):

    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
# =================================================================
# ESTUDIANTE 
# =================================================================
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

    return render(request, 'estudiante/base_estudiante.html')

def perfil_estudiante(request):

    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        return render(request, 'estudiante/perfil_estudiante.html', {"usuario": usuario})
    except Usuario.DoesNotExist:
        return redirect('login')
# =================================================================
# COMPONENTES
# =================================================================

def componentes_list(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    # Manejar cambio de estado vía POST (AJAX o formulario)
    if request.method == 'POST' and request.POST.get('cambiar_estado') == '1':
        componente_id = request.POST.get('componente_id')
        try:
            componente = get_object_or_404(Componente, pk=componente_id)
            componente.estado = 'Inactivo' if componente.estado == 'Activo' else 'Activo'
            componente.save()
            # Si es petición AJAX, responder JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'estado': componente.estado})
            messages.success(request, f"Estado cambiado a {componente.estado} correctamente.")
            return redirect('componentes_list')
        except Exception as e:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, f"Error al cambiar estado: {str(e)}")
            return redirect('componentes_list')
    q = request.GET.get('q', '').strip()
    qs = Componente.objects.select_related('laboratorio').all().order_by('nombre')
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q) | Q(laboratorio__nombre__icontains=q))

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

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

    if request.method == 'POST':
        form = ComponenteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Componente creado correctamente')
            if is_ajax:
                return JsonResponse({'success': True, 'redirect': reverse('componentes_list')})
            return redirect('componentes_list')
        else:
            if is_ajax:
                # devolver el partial con errores para reemplazar el contenido del modal
                html = render_to_string('administrador/_componente_form_partial.html', {'form': form, 'accion': 'Agregar'}, request=request)
                return JsonResponse({'success': False, 'html': html})
    else:
        form = ComponenteForm()

    # Si es petición AJAX GET, devolver sólo el partial (la tarjeta/modal)
    if is_ajax and request.method == 'GET':
        html = render_to_string('administrador/_componente_form_partial.html', {'form': form, 'accion': 'Agregar'}, request=request)
        return HttpResponse(html)

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
    qs = Componente.objects.select_related('laboratorio').all().order_by('nombre')
    
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


### --- VISTAS ESTUDIANTES (INTERFAZ) --- ###ESTE si

def estudiantes_laboratorios_list(request):
    # lista pública (o basada en sesión) de laboratorios disponibles
    labs = Laboratorio.objects.filter(estado='activo')
    return render(request, 'estudiante/laboratorios.html', {'laboratorios': labs})


def laboratorio_access_confirm(request, pk):
    lab = get_object_or_404(Laboratorio, pk=pk)
    return render(request, 'estudiante/laboratorio_confirm.html', {'laboratorio': lab})


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
    return render(request, 'estudiante/laboratorio_view.html', {'laboratorio': lab, 'html_url': html_url})




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
                            _shutil.copyfileobj(source, target)

                os.remove(tmp_zip_path)

                # --- NUEVO: buscar carpeta que contenga index.html ---
                final_carpeta = target_dir
                for root, dirs, files in os.walk(target_dir):
                    if 'index.html' in files:
                        final_carpeta = root
                        break

                # guardar la ruta relativa
                lab.carpeta = os.path.relpath(final_carpeta, settings.MEDIA_ROOT)
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
        if not usuario.rol or usuario.rol.tipo.strip() != 'SuperAdmin':
            messages.error(request, 'No tiene permisos para acceder a esta página')
            return redirect('login')
        
        # FILTRO ÚNICO DE FECHA
        fecha_filtro = request.GET.get('fecha', '')
        filtro_colegio = request.GET.get('colegio', '')
        
        # Consultas base
        colegios_query = Colegio.objects.all()
        usuarios_query = Usuario.objects.all()
        estudiantes_query = Estudiante.objects.all()
        profesores_query = Profesor.objects.all()
        suscripciones_query = Suscripcion.objects.all()
        pagos_query = Pago.objects.filter(estado='aprobado')
        
        # Aplicar filtro de fecha única
        if fecha_filtro:
            try:
                fecha_dt = datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
                suscripciones_query = suscripciones_query.filter(
                    fecha_inicio__lte=fecha_dt,
                    fecha_fin__gte=fecha_dt
                )
                pagos_query = pagos_query.filter(fecha__date=fecha_dt)
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
            'fecha_filtro': fecha_filtro,
            'filtro_colegio': filtro_colegio,
        }
        
        return render(request, 'superadministrador/dashboard_superadmin.html', context)
        
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('panel_superadmin')

# ====================================================================
# DASHBOARD ADMINISTRADOR 
# ====================================================================
@login_required_custom
def dashboard_administrador(request):
    usuario_id = request.session.get('usuario_id')

    try:
        usuario = Usuario.objects.get(id=usuario_id)
        
        # Verificación de rol
        if not usuario.rol:
            messages.error(request, 'Usuario sin rol asignado')
            return redirect('login')

        rol_tipo = usuario.rol.tipo.strip()

        if rol_tipo not in ['Administrador', 'SuperAdmin']:
            messages.error(request, f'No tiene permisos para acceder al dashboard.')
            return redirect('login')

        # Perfil de administrador y colegio
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
                    'datos_torta_cursos': json.dumps([{'name': 'Sin datos', 'y': 1}]),
                    'datos_barras_cursos': json.dumps({'cursos': ['Sin datos'], 'estudiantes': [0]}),
                    'estudiantes_recientes': [],
                    'profesores': [],
                }
                return render(request, 'administrador/dashboard_administrador.html', context)

        # FILTRO ÚNICO DE FECHA
        fecha_filtro = request.GET.get('fecha', '')

        # Consultas base
        estudiantes_query = Estudiante.objects.filter(colegio=colegio_admin)
        profesores_query = Profesor.objects.filter(colegio=colegio_admin)
        cursos_query = Curso.objects.filter(profesor__colegio=colegio_admin)

        suscripcion_query = Suscripcion.objects.filter(
            colegio=colegio_admin,
            fecha_fin__gte=timezone.now().date()
        ).first()

        # Aplicar filtro de fecha si existe
        if fecha_filtro:
            try:
                fecha_dt = datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
                # Filtrar estudiantes creados hasta esa fecha (si tienes campo de fecha)
                # estudiantes_query = estudiantes_query.filter(fecha_creacion__lte=fecha_dt)
            except ValueError:
                messages.error(request, 'Formato de fecha inválido')

        # Estadísticas principales
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
            estadisticas = {
                'total_estudiantes': 0,
                'total_profesores': 0,
                'total_cursos': 0,
                'membresia_actual': 'Error en datos',
                'usuarios_actuales': 0,
                'dias_restantes': 0,
            }

        # Gráfico de torta - Estudiantes por curso (CORREGIDO)
        try:
            # SOLUCIÓN: Obtener datos de manera diferente para evitar el error
            cursos_con_estudiantes = []
            for curso in Curso.objects.filter(profesor__colegio=colegio_admin):
                total_estudiantes = estudiantes_query.filter(curso=curso).count()
                if total_estudiantes > 0:
                    cursos_con_estudiantes.append({
                        'curso_nombre': curso.nombre,
                        'total': total_estudiantes
                    })
            
            cursos_con_estudiantes.sort(key=lambda x: x['total'], reverse=True)
            
            if cursos_con_estudiantes:
                datos_torta_cursos = [
                    {'name': item['curso_nombre'], 'y': item['total']}
                    for item in cursos_con_estudiantes
                ]
            else:
                datos_torta_cursos = [{'name': 'Sin estudiantes', 'y': 1}]
        except Exception as e:
            print(f"Error en gráfico de torta: {e}")
            datos_torta_cursos = [{'name': 'Error en datos', 'y': 1}]

        # Gráfico de barras - Cursos con más estudiantes (CORREGIDO)
        try:
            # SOLUCIÓN: Usar la misma lógica corregida
            if cursos_con_estudiantes:
                datos_barras_cursos = {
                    'cursos': [item['curso_nombre'][:20] + '...' if len(item['curso_nombre']) > 20 else item['curso_nombre'] 
                              for item in cursos_con_estudiantes[:5]],
                    'estudiantes': [item['total'] for item in cursos_con_estudiantes[:5]]
                }
            else:
                datos_barras_cursos = {'cursos': ['Sin datos'], 'estudiantes': [0]}
        except Exception as e:
            print(f"Error en gráfico de barras: {e}")
            datos_barras_cursos = {'cursos': ['Error en datos'], 'estudiantes': [0]}

        # Tablas
        try:
            estudiantes_recientes = estudiantes_query.select_related('persona', 'colegio').order_by('-id')[:10]
        except:
            estudiantes_recientes = []

        try:
            profesores_lista = profesores_query.select_related('usuario', 'colegio').order_by('usuario__correo')
        except:
            profesores_lista = []

        context = {
            'usuario': usuario,
            'administrador': administrador,
            'colegio': colegio_admin,
            'estadisticas': estadisticas,
            'datos_torta_cursos': json.dumps(datos_torta_cursos),
            'datos_barras_cursos': json.dumps(datos_barras_cursos),
            'estudiantes_recientes': estudiantes_recientes,
            'profesores': profesores_lista,
            'fecha_filtro': fecha_filtro,
        }

        return render(request, 'administrador/dashboard_administrador.html', context)

    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('login')
    except Exception as e:
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
        if not usuario.rol or usuario.rol.tipo.strip() != 'Profesor':
            messages.error(request, 'No tiene permisos para acceder a esta página')
            return redirect('login')
        
        # Obtener el profesor
        profesor = Profesor.objects.filter(usuario=usuario).first()
        
        if not profesor:
            messages.warning(request, 'Perfil de profesor no encontrado')
            context = {
                'usuario': usuario,
                'profesor': None,
                'estadisticas': {
                    'total_cursos': 0,
                    'total_temas': 0,
                    'temas_disponibles': 0,
                    'temas_no_disponibles': 0,
                },
                'datos_torta_temas': json.dumps([{'name': 'Sin datos', 'y': 1}]),
                'datos_barras_temas': json.dumps({'cursos': ['Sin datos'], 'temas': [0]}),
                'temas_recientes': [],
                'cursos': [],
            }
            return render(request, 'profesor/dashboard_profesor.html', context)
        
        # FILTRO ÚNICO DE FECHA
        fecha_filtro = request.GET.get('fecha', '')
        
        # Consultas base del profesor CON ANNOTATE
        cursos_query = Curso.objects.filter(profesor=profesor).annotate(total_temas=Count('temas'))
        temas_query = Temas.objects.filter(curso__profesor=profesor)
        
        # Aplicar filtro de fecha si existe
        if fecha_filtro:
            try:
                fecha_dt = datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
                temas_query = temas_query.filter(fecha_inicio__lte=fecha_dt)
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
        if estadisticas['temas_disponibles'] > 0 or estadisticas['temas_no_disponibles'] > 0:
            datos_torta_temas = [
                {'name': 'Disponibles', 'y': estadisticas['temas_disponibles']},
                {'name': 'No Disponibles', 'y': estadisticas['temas_no_disponibles']},
            ]
        else:
            datos_torta_temas = [{'name': 'Sin temas', 'y': 1}]
        
        # GRÁFICO DE BARRAS - Temas por curso
        if cursos_query.exists():
            datos_barras_temas = {
                'cursos': [curso.nombre for curso in cursos_query],
                'temas': [curso.total_temas for curso in cursos_query]
            }
        else:
            datos_barras_temas = {'cursos': ['Sin cursos'], 'temas': [0]}
        
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
            'fecha_filtro': fecha_filtro,
        }
        
        return render(request, 'profesor/dashboard_profesor.html', context)
        
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('panel_profesor')


def dashboard_estudiante(request):
    return render(request, 'estudiante/dashboard_estudiante.html')

# ====================================================================
# GENERAR REPORTE PDF COMPLETO 
# ====================================================================
@login_required_custom
def generar_reporte_completo_pdf(request):
    """Genera un PDF completo con todos los datos del dashboard según el rol"""
    usuario_id = request.session.get('usuario_id')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        rol = usuario.rol.tipo.strip() if usuario.rol else ''
        
        # Crear el buffer y documento PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []
        styles = getSampleStyleSheet()
        
        # Estilo personalizado para el título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=1  # Centrado
        )
        
        # Estilo para subtítulos
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # ENCABEZADO DEL REPORTE
        if rol == 'SuperAdmin':
            titulo = "INFORME GENERAL DEL SISTEMA"
        elif rol == 'Administrador':
            titulo = "INFORME ADMINISTRATIVO"
        elif rol == 'Profesor':
            titulo = "INFORME ACADÉMICO"
        else:
            titulo = "INFORME"
        
        elements.append(Paragraph(titulo, title_style))
        elements.append(Paragraph(f"<b>Generado por:</b> {usuario.correo}", styles['Normal']))
        elements.append(Paragraph(f"<b>Fecha:</b> {timezone.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # CONTENIDO SEGÚN ROL
        if rol == 'SuperAdmin':
            elements.extend(generar_contenido_superadmin_pdf(usuario, subtitle_style, styles))
        elif rol == 'Administrador':
            elements.extend(generar_contenido_administrador_pdf(usuario, subtitle_style, styles))
        elif rol == 'Profesor':
            elements.extend(generar_contenido_profesor_pdf(usuario, subtitle_style, styles))
        else:
            elements.append(Paragraph("No hay datos disponibles para su rol", styles['Normal']))
        
        # Generar PDF
        try:
            doc.build(elements)
            buffer.seek(0)
            
            # Crear respuesta HTTP
            filename = f'informe_{rol.lower()}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            messages.error(request, f'Error al construir el PDF: {str(e)}')
            return redirect('dashboard_administrador')
        
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'Error al generar el reporte: {str(e)}')
        return redirect('dashboard_administrador')

# ====================================================================
# FUNCIONES AUXILIARES PARA GENERAR CONTENIDO PDF (MEJORADAS)
# ====================================================================
def generar_contenido_superadmin_pdf(usuario, subtitle_style, styles):
    """Genera el contenido completo y extendido del PDF para SuperAdmin"""
    elements = []
    
    # ===== SECCIÓN 1: ESTADÍSTICAS GENERALES =====
    elements.append(Paragraph("1. ESTADÍSTICAS GENERALES DEL SISTEMA", subtitle_style))
    
    try:
        colegios_count = Colegio.objects.count()
        usuarios_count = Usuario.objects.count()
        estudiantes_count = Estudiante.objects.count()
        profesores_count = Profesor.objects.count()
        suscripciones_count = Suscripcion.objects.count()
        suscripciones_activas = Suscripcion.objects.filter(fecha_fin__gte=timezone.now().date()).count()
        suscripciones_vencidas = Suscripcion.objects.filter(fecha_fin__lt=timezone.now().date()).count()
        total_ingresos = Pago.objects.filter(estado='aprobado').aggregate(total=Sum('monto'))['total'] or 0
        total_pagos = Pago.objects.filter(estado='aprobado').count()
        
        data_estadisticas = [
            ['Métrica', 'Cantidad'],
            ['Total de Colegios Registrados', str(colegios_count)],
            ['Total de Usuarios en el Sistema', str(usuarios_count)],
            ['Total de Estudiantes', str(estudiantes_count)],
            ['Total de Profesores', str(profesores_count)],
            ['Total de Suscripciones', str(suscripciones_count)],
            ['Suscripciones Activas', str(suscripciones_activas)],
            ['Suscripciones Vencidas', str(suscripciones_vencidas)],
            ['Total de Pagos Aprobados', str(total_pagos)],
            ['Ingresos Totales Generados', f'${float(total_ingresos):,.2f}'],
        ]
        
        table_estadisticas = Table(data_estadisticas, colWidths=[350, 150])
        table_estadisticas.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        elements.append(table_estadisticas)
    except Exception as e:
        elements.append(Paragraph(f"Error al cargar estadísticas generales: {str(e)}", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # ===== SECCIÓN 2: DISTRIBUCIÓN DE USUARIOS POR ROL =====
    elements.append(Paragraph("2. DISTRIBUCIÓN DE USUARIOS POR ROL", subtitle_style))
    
    try:
        distribucion_roles = Usuario.objects.values('rol__tipo').annotate(
            total=Count('id')
        ).order_by('-total')
        
        data_roles = [['Rol', 'Cantidad de Usuarios', 'Porcentaje']]
        total_usuarios = Usuario.objects.count()
        
        for item in distribucion_roles:
            nombre_rol = item['rol__tipo'] if item['rol__tipo'] else 'Sin rol asignado'
            cantidad = item['total']
            porcentaje = (cantidad / total_usuarios * 100) if total_usuarios > 0 else 0
            data_roles.append([nombre_rol, str(cantidad), f"{porcentaje:.1f}%"])
        
        if len(data_roles) > 1:
            table_roles = Table(data_roles, colWidths=[250, 150, 100])
            table_roles.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(table_roles)
        else:
            elements.append(Paragraph("No hay datos disponibles de roles", styles['Normal']))
    except Exception as e:
        elements.append(Paragraph("Error al cargar distribución de roles", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # ===== SECCIÓN 3: TOP 10 COLEGIOS CON MÁS ESTUDIANTES =====
    elements.append(Paragraph("3. TOP 10 COLEGIOS CON MÁS ESTUDIANTES", subtitle_style))
    
    try:
        top_colegios = Colegio.objects.annotate(
            total_estudiantes=Count('estudiantes'),
            total_profesores=Count('profesores')
        ).order_by('-total_estudiantes')[:10]
        
        data_colegios = [['#', 'Nombre del Colegio', 'Estudiantes', 'Profesores']]
        
        for idx, colegio in enumerate(top_colegios, 1):
            nombre_corto = colegio.nombre[:35] + '...' if len(colegio.nombre) > 35 else colegio.nombre
            data_colegios.append([
                str(idx),
                nombre_corto,
                str(colegio.total_estudiantes),
                str(colegio.total_profesores)
            ])
        
        if len(data_colegios) > 1:
            table_colegios = Table(data_colegios, colWidths=[30, 300, 80, 80])
            table_colegios.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            elements.append(table_colegios)
        else:
            elements.append(Paragraph("No hay colegios registrados", styles['Normal']))
    except Exception as e:
        elements.append(Paragraph("Error al cargar ranking de colegios", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # ===== SECCIÓN 4: DISTRIBUCIÓN DE SUSCRIPCIONES POR TIPO DE MEMBRESÍA =====
    elements.append(Paragraph("4. DISTRIBUCIÓN DE SUSCRIPCIONES POR MEMBRESÍA", subtitle_style))
    
    try:
        membresias = Membresia.objects.annotate(
            total_suscripciones=Count('suscripciones'),
            activas=Count('suscripciones', filter=Q(suscripciones__fecha_fin__gte=timezone.now().date())),
            vencidas=Count('suscripciones', filter=Q(suscripciones__fecha_fin__lt=timezone.now().date()))
        ).order_by('-total_suscripciones')
        
        data_membresias = [['Tipo de Membresía', 'Total', 'Activas', 'Vencidas', 'Precio']]
        
        for membresia in membresias:
            data_membresias.append([
                membresia.nombre,
                str(membresia.total_suscripciones),
                str(membresia.activas),
                str(membresia.vencidas),
                f'${float(membresia.precio):,.2f}'
            ])
        
        if len(data_membresias) > 1:
            table_membresias = Table(data_membresias, colWidths=[180, 80, 80, 80, 80])
            table_membresias.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16a085')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            elements.append(table_membresias)
        else:
            elements.append(Paragraph("No hay membresías registradas", styles['Normal']))
    except Exception as e:
        elements.append(Paragraph("Error al cargar distribución de membresías", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # ===== SECCIÓN 5: ÚLTIMAS 15 SUSCRIPCIONES REGISTRADAS =====
    elements.append(Paragraph("5. ÚLTIMAS 15 SUSCRIPCIONES REGISTRADAS", subtitle_style))
    
    try:
        suscripciones_recientes = Suscripcion.objects.select_related(
            'colegio', 'membresia'
        ).order_by('-fecha_inicio')[:15]
        
        data_suscripciones = [['Colegio', 'Membresía', 'Inicio', 'Fin', 'Estado']]
        
        for sus in suscripciones_recientes:
            nombre_colegio = sus.colegio.nombre[:25] + '...' if len(sus.colegio.nombre) > 25 else sus.colegio.nombre
            estado = 'ACTIVA' if sus.fecha_fin >= timezone.now().date() else 'VENCIDA'
            color_estado = 'green' if estado == 'ACTIVA' else 'red'
            
            data_suscripciones.append([
                nombre_colegio,
                sus.membresia.nombre,
                sus.fecha_inicio.strftime('%d/%m/%Y'),
                sus.fecha_fin.strftime('%d/%m/%Y'),
                estado
            ])
        
        if len(data_suscripciones) > 1:
            table_suscripciones = Table(data_suscripciones, colWidths=[160, 100, 80, 80, 80])
            table_suscripciones.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            elements.append(table_suscripciones)
        else:
            elements.append(Paragraph("No hay suscripciones registradas", styles['Normal']))
    except Exception as e:
        elements.append(Paragraph("Error al cargar suscripciones recientes", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # ===== SECCIÓN 6: ÚLTIMOS 15 PAGOS APROBADOS =====
    elements.append(Paragraph("6. ÚLTIMOS 15 PAGOS APROBADOS", subtitle_style))
    
    try:
        pagos_recientes = Pago.objects.filter(estado='aprobado').select_related(
            'usuario'
        ).order_by('-fecha')[:15]
        
        data_pagos = [['Fecha', 'Usuario', 'Monto', 'Método', 'Referencia']]
        
        for pago in pagos_recientes:
            data_pagos.append([
                pago.fecha.strftime('%d/%m/%Y %H:%M'),
                pago.usuario.correo[:30] if pago.usuario else 'N/A',
                f'${float(pago.monto):,.2f}',
                pago.metodo_pago if hasattr(pago, 'metodo_pago') else 'N/A',
                str(pago.referencia_pago)[:15] if hasattr(pago, 'referencia_pago') else 'N/A'
            ])
        
        if len(data_pagos) > 1:
            table_pagos = Table(data_pagos, colWidths=[100, 150, 80, 80, 90])
            table_pagos.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            elements.append(table_pagos)
        else:
            elements.append(Paragraph("No hay pagos registrados", styles['Normal']))
    except Exception as e:
        elements.append(Paragraph("Error al cargar pagos recientes", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # ===== SECCIÓN 7: RESUMEN FINANCIERO =====
    elements.append(Paragraph("7. RESUMEN FINANCIERO", subtitle_style))
    
    try:
        ingresos_totales = Pago.objects.filter(estado='aprobado').aggregate(total=Sum('monto'))['total'] or 0
        pagos_pendientes = Pago.objects.filter(estado='pendiente').count()
        pagos_rechazados = Pago.objects.filter(estado='rechazado').count()
        pagos_aprobados = Pago.objects.filter(estado='aprobado').count()
        
        # Ingresos por membresía
        ingresos_membresias = Suscripcion.objects.values('membresia__nombre').annotate(
            ingresos=Sum('membresia__precio')
        ).order_by('-ingresos')
        
        data_financiero = [['Concepto', 'Valor']]
        data_financiero.append(['Total Ingresos Generados', f'${float(ingresos_totales):,.2f}'])
        data_financiero.append(['Pagos Aprobados', str(pagos_aprobados)])
        data_financiero.append(['Pagos Pendientes', str(pagos_pendientes)])
        data_financiero.append(['Pagos Rechazados', str(pagos_rechazados)])
        
        table_financiero = Table(data_financiero, colWidths=[350, 150])
        table_financiero.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        elements.append(table_financiero)
    except Exception as e:
        elements.append(Paragraph("Error al cargar resumen financiero", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    return elements

def generar_contenido_administrador_pdf(usuario, subtitle_style, styles):
    """Genera el contenido completo y extendido del PDF para Administrador"""
    elements = []
    
    # Obtener colegio del administrador
    try:
        administrador = Administrador.objects.filter(usuario=usuario).first()
        if administrador and administrador.colegio:
            colegio_admin = administrador.colegio
        else:
            colegio_admin = Colegio.objects.first()
        
        if not colegio_admin:
            elements.append(Paragraph("No hay colegio asignado", styles['Normal']))
            return elements
        
        elements.append(Paragraph(f"COLEGIO: {colegio_admin.nombre}", subtitle_style))
        elements.append(Paragraph(f"<b>Dirección:</b> {colegio_admin.direccion if hasattr(colegio_admin, 'direccion') else 'N/A'}", styles['Normal']))
        elements.append(Spacer(1, 10))
        
        # ===== SECCIÓN 1: ESTADÍSTICAS GENERALES DEL COLEGIO =====
        elements.append(Paragraph("1. ESTADÍSTICAS GENERALES DEL COLEGIO", subtitle_style))
        
        estudiantes_query = Estudiante.objects.filter(colegio=colegio_admin)
        profesores_query = Profesor.objects.filter(colegio=colegio_admin)
        cursos_query = Curso.objects.filter(profesor__colegio=colegio_admin)
        
        suscripcion = Suscripcion.objects.filter(
            colegio=colegio_admin,
            fecha_fin__gte=timezone.now().date()
        ).first()
        
        dias_restantes = 0
        if suscripcion:
            dias_restantes = max((suscripcion.fecha_fin - timezone.now().date()).days, 0)
        
        data_estadisticas = [
            ['Métrica', 'Cantidad'],
            ['Total Estudiantes Registrados', str(estudiantes_query.count())],
            ['Total Profesores Activos', str(profesores_query.count())],
            ['Total Cursos Disponibles', str(cursos_query.count())],
            ['Membresía Actual', suscripcion.membresia.nombre if suscripcion else 'Sin membresía activa'],
            ['Usuarios Actuales en Plataforma', str(suscripcion.usuarios_actuales if suscripcion else 0)],
            ['Días Restantes de Membresía', str(dias_restantes)],
            ['Fecha Inicio Suscripción', suscripcion.fecha_inicio.strftime('%d/%m/%Y') if suscripcion else 'N/A'],
            ['Fecha Fin Suscripción', suscripcion.fecha_fin.strftime('%d/%m/%Y') if suscripcion else 'N/A'],
        ]
        
        table_estadisticas = Table(data_estadisticas, colWidths=[350, 150])
        table_estadisticas.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        elements.append(table_estadisticas)
        
    except Exception as e:
        elements.append(Paragraph(f"Error al cargar datos del colegio: {str(e)}", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # ===== SECCIÓN 2: DISTRIBUCIÓN DE ESTUDIANTES POR CURSO =====
    elements.append(Paragraph("2. DISTRIBUCIÓN DE ESTUDIANTES POR CURSO", subtitle_style))
    
    try:
        estudiantes_query = Estudiante.objects.filter(colegio=colegio_admin)
        cursos_con_estudiantes = []
        
        for curso in Curso.objects.filter(profesor__colegio=colegio_admin):
            total_estudiantes = estudiantes_query.filter(curso=curso).count()
            profesor_nombre = curso.profesor.usuario.correo if curso.profesor and curso.profesor.usuario else 'Sin profesor'
            cursos_con_estudiantes.append({
                'curso_nombre': curso.nombre,
                'profesor': profesor_nombre,
                'total': total_estudiantes
            })
        
        cursos_con_estudiantes.sort(key=lambda x: x['total'], reverse=True)
        
        data_cursos = [['Curso', 'Profesor', 'Total Estudiantes']]
        for item in cursos_con_estudiantes:
            nombre_curso = item['curso_nombre'][:30] + '...' if len(item['curso_nombre']) > 30 else item['curso_nombre']
            nombre_prof = item['profesor'][:25] + '...' if len(item['profesor']) > 25 else item['profesor']
            data_cursos.append([nombre_curso, nombre_prof, str(item['total'])])
        
        if len(data_cursos) > 1:
            table_cursos = Table(data_cursos, colWidths=[200, 200, 100])
            table_cursos.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            elements.append(table_cursos)
        else:
            elements.append(Paragraph("No hay cursos con estudiantes asignados", styles['Normal']))
            
    except Exception as e:
        elements.append(Paragraph("Error al cargar distribución por cursos", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # ===== SECCIÓN 3: LISTADO DE PROFESORES =====
    elements.append(Paragraph("3. LISTADO COMPLETO DE PROFESORES", subtitle_style))
    
    try:
        profesores_lista = Profesor.objects.filter(colegio=colegio_admin).select_related('usuario')
        
        data_profesores = [['#', 'Correo Electrónico', 'Cursos Asignados']]
        
        for idx, profesor in enumerate(profesores_lista, 1):
            cursos_count = Curso.objects.filter(profesor=profesor).count()
            correo = profesor.usuario.correo if profesor.usuario else 'Sin correo'
            correo_corto = correo[:35] + '...' if len(correo) > 35 else correo
            data_profesores.append([str(idx), correo_corto, str(cursos_count)])
        
        if len(data_profesores) > 1:
            table_profesores = Table(data_profesores, colWidths=[30, 370, 100])
            table_profesores.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            elements.append(table_profesores)
        else:
            elements.append(Paragraph("No hay profesores registrados en este colegio", styles['Normal']))
    except Exception as e:
        elements.append(Paragraph("Error al cargar listado de profesores", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # ===== SECCIÓN 4: ÚLTIMOS 20 ESTUDIANTES REGISTRADOS =====
    elements.append(Paragraph("4. ÚLTIMOS 20 ESTUDIANTES REGISTRADOS", subtitle_style))
    
    try:
        estudiantes_recientes = Estudiante.objects.filter(
            colegio=colegio_admin
        ).select_related('persona', 'curso').order_by('-id')[:20]
        
        data_estudiantes = [['#', 'Nombre Completo', 'Curso Asignado']]
        
        for idx, estudiante in enumerate(estudiantes_recientes, 1):
            if estudiante.persona:
                nombre_completo = f"{estudiante.persona.nombre} {estudiante.persona.apellido_paterno}"
                nombre_corto = nombre_completo[:30] + '...' if len(nombre_completo) > 30 else nombre_completo
            else:
                nombre_corto = "Sin información"
            
            curso_nombre = estudiante.curso.nombre[:25] if estudiante.curso else 'Sin curso'
            data_estudiantes.append([str(idx), nombre_corto, curso_nombre])
        
        if len(data_estudiantes) > 1:
            table_estudiantes = Table(data_estudiantes, colWidths=[30, 300, 170])
            table_estudiantes.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16a085')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            elements.append(table_estudiantes)
        else:
            elements.append(Paragraph("No hay estudiantes registrados recientemente", styles['Normal']))
    except Exception as e:
        elements.append(Paragraph("Error al cargar estudiantes recientes", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # ===== SECCIÓN 5: HISTORIAL DE SUSCRIPCIONES DEL COLEGIO =====
    elements.append(Paragraph("5. HISTORIAL DE SUSCRIPCIONES", subtitle_style))
    
    try:
        historial_suscripciones = Suscripcion.objects.filter(
            colegio=colegio_admin
        ).select_related('membresia').order_by('-fecha_inicio')
        
        data_historial = [['Membresía', 'Fecha Inicio', 'Fecha Fin', 'Duración', 'Estado']]
        
        for sus in historial_suscripciones:
            duracion_dias = (sus.fecha_fin - sus.fecha_inicio).days
            estado = 'ACTIVA' if sus.fecha_fin >= timezone.now().date() else 'VENCIDA'
            
            data_historial.append([
                sus.membresia.nombre,
                sus.fecha_inicio.strftime('%d/%m/%Y'),
                sus.fecha_fin.strftime('%d/%m/%Y'),
                f"{duracion_dias} días",
                estado
            ])
        
        if len(data_historial) > 1:
            table_historial = Table(data_historial, colWidths=[120, 90, 90, 90, 110])
            table_historial.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            elements.append(table_historial)
        else:
            elements.append(Paragraph("No hay historial de suscripciones", styles['Normal']))
    except Exception as e:
        elements.append(Paragraph("Error al cargar historial de suscripciones", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # ===== SECCIÓN 6: PROYECCIÓN Y ALERTAS =====
    elements.append(Paragraph("6. PROYECCIÓN Y ALERTAS", subtitle_style))
    
    try:
        alertas_texto = []
        
        if suscripcion:
            if dias_restantes <= 7 and dias_restantes > 0:
                alertas_texto.append(f"ATENCIÓN: La membresía vence en {dias_restantes} días. Se recomienda renovar pronto.")
            elif dias_restantes == 0:
                alertas_texto.append("URGENTE: La membresía vence hoy. Renovar inmediatamente.")
            elif dias_restantes < 0:
                alertas_texto.append(f"CRÍTICO: La membresía venció hace {abs(dias_restantes)} días. Acceso suspendido.")
            else:
                alertas_texto.append(f"✓ La membresía está activa y vence en {dias_restantes} días.")
        else:
            alertas_texto.append("No hay membresía activa. El colegio no tiene acceso a la plataforma.")
        
        # Alertas adicionales
        if estudiantes_query.count() == 0:
            alertas_texto.append("No hay estudiantes registrados en el sistema.")
        
        if profesores_query.count() == 0:
            alertas_texto.append("No hay profesores asignados al colegio.")
        
        if cursos_query.count() == 0:
            alertas_texto.append("No hay cursos creados en el sistema.")
        
        for alerta in alertas_texto:
            elements.append(Paragraph(alerta, styles['Normal']))
            elements.append(Spacer(1, 5))
        
    except Exception as e:
        elements.append(Paragraph("Error al generar alertas", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    return elements

def generar_contenido_profesor_pdf(usuario, subtitle_style, styles):
    """Genera el contenido completo y extendido del PDF para Profesor"""
    elements = []
    
    try:
        # Obtener el profesor
        profesor = Profesor.objects.filter(usuario=usuario).first()
        
        if not profesor:
            elements.append(Paragraph("Perfil de profesor no encontrado", styles['Normal']))
            return elements
        
        elements.append(Paragraph(f"PROFESOR: {usuario.correo}", subtitle_style))
        if profesor.colegio:
            elements.append(Paragraph(f"<b>Colegio:</b> {profesor.colegio.nombre}", styles['Normal']))
        elements.append(Spacer(1, 10))
        
        # ===== SECCIÓN 1: ESTADÍSTICAS GENERALES DEL PROFESOR =====
        elements.append(Paragraph("1. ESTADÍSTICAS GENERALES", subtitle_style))
        
        cursos_query = Curso.objects.filter(profesor=profesor)
        temas_query = Temas.objects.filter(curso__profesor=profesor)
        
        temas_disponibles = temas_query.filter(estado='disponible').count()
        temas_no_disponibles = temas_query.filter(estado='no disponible').count()
        
        # Contar estudiantes totales
        total_estudiantes = 0
        for curso in cursos_query:
            total_estudiantes += Estudiante.objects.filter(curso=curso).count()
        
        data_estadisticas = [
            ['Métrica', 'Cantidad'],
            ['Total de Cursos Asignados', str(cursos_query.count())],
            ['Total de Temas Creados', str(temas_query.count())],
            ['Temas Disponibles', str(temas_disponibles)],
            ['Temas No Disponibles', str(temas_no_disponibles)],
            ['Total de Estudiantes', str(total_estudiantes)],
        ]
        
        table_estadisticas = Table(data_estadisticas, colWidths=[350, 150])
        table_estadisticas.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        elements.append(table_estadisticas)
        
    except Exception as e:
        elements.append(Paragraph(f"Error al cargar datos del profesor: {str(e)}", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # ===== SECCIÓN 2: DISTRIBUCIÓN DE TEMAS POR ESTADO =====
    elements.append(Paragraph("2. DISTRIBUCIÓN DE TEMAS POR ESTADO", subtitle_style))
    
    try:
        temas_por_estado = temas_query.values('estado').annotate(
            total=Count('id')
        ).order_by('-total')
        
        data_estados = [['Estado', 'Cantidad de Temas', 'Porcentaje']]
        total_temas = temas_query.count()
        
        for item in temas_por_estado:
            estado = item['estado'] if item['estado'] else 'Sin estado'
            cantidad = item['total']
            porcentaje = (cantidad / total_temas * 100) if total_temas > 0 else 0
            data_estados.append([estado.title(), str(cantidad), f"{porcentaje:.1f}%"])
        
        if len(data_estados) > 1:
            table_estados = Table(data_estados, colWidths=[250, 150, 100])
            table_estados.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            elements.append(table_estados)
        else:
            elements.append(Paragraph("No hay datos de estados de temas", styles['Normal']))
    except Exception as e:
        elements.append(Paragraph("Error al cargar distribución de estados", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # ===== SECCIÓN 3: DETALLE DE CURSOS Y TEMAS =====
    elements.append(Paragraph("3. DETALLE DE CURSOS Y CANTIDAD DE TEMAS", subtitle_style))
    
    try:
        cursos_detalle = Curso.objects.filter(profesor=profesor).annotate(
            total_temas=Count('temas'),
            temas_disponibles=Count('temas', filter=Q(temas__estado='disponible')),
            temas_no_disponibles=Count('temas', filter=Q(temas__estado='no disponible')),
            total_estudiantes=Count('estudiantes')
        ).order_by('-total_temas')
        
        data_cursos = [['Curso', 'Total Temas', 'Disponibles', 'No Disponibles', 'Estudiantes']]
        
        for curso in cursos_detalle:
            nombre_curso = curso.nombre[:35] + '...' if len(curso.nombre) > 35 else curso.nombre
            data_cursos.append([
                nombre_curso,
                str(curso.total_temas),
                str(curso.temas_disponibles),
                str(curso.temas_no_disponibles),
                str(curso.total_estudiantes)
            ])
        
        if len(data_cursos) > 1:
            table_cursos = Table(data_cursos, colWidths=[220, 70, 70, 80, 70])
            table_cursos.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            elements.append(table_cursos)
        else:
            elements.append(Paragraph("No hay cursos asignados al profesor", styles['Normal']))
    except Exception as e:
        elements.append(Paragraph("Error al cargar detalle de cursos", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # ===== SECCIÓN 4: ÚLTIMOS 20 TEMAS CREADOS =====
    elements.append(Paragraph("4. ÚLTIMOS 20 TEMAS CREADOS", subtitle_style))
    
    try:
        temas_recientes = Temas.objects.filter(
            curso__profesor=profesor
        ).select_related('curso').order_by('-fecha_inicio')[:20]
        
        data_temas = [['Tema', 'Curso', 'Fecha Inicio', 'Fecha Fin', 'Estado']]
        
        for tema in temas_recientes:
            nombre_tema = tema.nombre[:30] + '...' if len(tema.nombre) > 30 else tema.nombre
            nombre_curso = tema.curso.nombre[:25] + '...' if len(tema.curso.nombre) > 25 else tema.curso.nombre
            fecha_inicio = tema.fecha_inicio.strftime('%d/%m/%Y') if tema.fecha_inicio else 'N/A'
            fecha_fin = tema.fecha_fin.strftime('%d/%m/%Y') if tema.fecha_fin else 'N/A'
            estado = tema.estado.title() if tema.estado else 'N/A'
            
            data_temas.append([
                nombre_tema,
                nombre_curso,
                fecha_inicio,
                fecha_fin,
                estado
            ])
        
        if len(data_temas) > 1:
            table_temas = Table(data_temas, colWidths=[140, 130, 80, 80, 80])
            table_temas.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16a085')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            elements.append(table_temas)
        else:
            elements.append(Paragraph("No hay temas creados recientemente", styles['Normal']))
    except Exception as e:
        elements.append(Paragraph("Error al cargar temas recientes", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # ===== SECCIÓN 5: TEMAS PRÓXIMOS A INICIAR =====
    elements.append(Paragraph("5. TEMAS PRÓXIMOS A INICIAR (Siguientes 30 días)", subtitle_style))
    
    try:
        fecha_actual = timezone.now().date()
        fecha_limite = fecha_actual + timedelta(days=30)
        
        temas_proximos = Temas.objects.filter(
            curso__profesor=profesor,
            fecha_inicio__gte=fecha_actual,
            fecha_inicio__lte=fecha_limite
        ).select_related('curso').order_by('fecha_inicio')
        
        data_proximos = [['Tema', 'Curso', 'Fecha Inicio', 'Días Restantes']]
        
        for tema in temas_proximos:
            nombre_tema = tema.nombre[:35] + '...' if len(tema.nombre) > 35 else tema.nombre
            nombre_curso = tema.curso.nombre[:30] + '...' if len(tema.curso.nombre) > 30 else tema.curso.nombre
            fecha_inicio = tema.fecha_inicio.strftime('%d/%m/%Y')
            dias_restantes = (tema.fecha_inicio - fecha_actual).days
            
            data_proximos.append([
                nombre_tema,
                nombre_curso,
                fecha_inicio,
                f"{dias_restantes} días"
            ])
        
        if len(data_proximos) > 1:
            table_proximos = Table(data_proximos, colWidths=[180, 160, 80, 90])
            table_proximos.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            elements.append(table_proximos)
        else:
            elements.append(Paragraph("No hay temas programados para los próximos 30 días", styles['Normal']))
    except Exception as e:
        elements.append(Paragraph("Error al cargar temas próximos", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # ===== SECCIÓN 6: RESUMEN POR CURSO =====
    elements.append(Paragraph("6. RESUMEN DETALLADO POR CURSO", subtitle_style))
    
    try:
        for curso in cursos_query:
            elements.append(Paragraph(f"<b>Curso:</b> {curso.nombre}", styles['Normal']))
            
            temas_curso = Temas.objects.filter(curso=curso)
            estudiantes_curso = Estudiante.objects.filter(curso=curso).count()
            
            info_curso = [
                f"• Total de temas: {temas_curso.count()}",
                f"• Temas disponibles: {temas_curso.filter(estado='disponible').count()}",
                f"• Temas no disponibles: {temas_curso.filter(estado='no disponible').count()}",
                f"• Total de estudiantes inscritos: {estudiantes_curso}",
            ]
            
            for info in info_curso:
                elements.append(Paragraph(info, styles['Normal']))
            
            elements.append(Spacer(1, 10))
            
    except Exception as e:
        elements.append(Paragraph("Error al cargar resumen por curso", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # ===== SECCIÓN 7: ALERTAS Y RECOMENDACIONES =====
    elements.append(Paragraph("7. ALERTAS Y RECOMENDACIONES", subtitle_style))
    
    try:
        alertas = []
        
        # Verificar cursos sin temas
        cursos_sin_temas = cursos_query.annotate(
            num_temas=Count('temas')
        ).filter(num_temas=0)
        
        if cursos_sin_temas.exists():
            alertas.append(f"Hay {cursos_sin_temas.count()} curso(s) sin temas asignados.")
        
        # Verificar temas sin fechas
        temas_sin_fechas = temas_query.filter(fecha_inicio__isnull=True)
        if temas_sin_fechas.exists():
            alertas.append(f"Hay {temas_sin_fechas.count()} tema(s) sin fecha de inicio configurada.")
        
        # Verificar temas vencidos
        temas_vencidos = temas_query.filter(
            fecha_fin__lt=timezone.now().date(),
            estado='disponible'
        )
        if temas_vencidos.exists():
            alertas.append(f"Hay {temas_vencidos.count()} tema(s) vencido(s) que aún están marcados como disponibles.")
        
        # Verificar cursos sin estudiantes
        cursos_sin_estudiantes = []
        for curso in cursos_query:
            if Estudiante.objects.filter(curso=curso).count() == 0:
                cursos_sin_estudiantes.append(curso.nombre)
        
        if cursos_sin_estudiantes:
            alertas.append(f"Hay {len(cursos_sin_estudiantes)} curso(s) sin estudiantes inscritos.")
        
        if not alertas:
            alertas.append("✓ No se encontraron alertas. Todo está en orden.")
        
        for alerta in alertas:
            elements.append(Paragraph(alerta, styles['Normal']))
            elements.append(Spacer(1, 5))
        
    except Exception as e:
        elements.append(Paragraph("Error al generar alertas", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    return elements

# ====================================================================
# VISTA PRINCIPAL DE INFORMES (Redirige según rol)
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
        else:
            messages.error(request, 'No tiene acceso al módulo de informes')
            return redirect('login')
            
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('login')
    
##VISTA PARA CONTENIDO TEORICO##

import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password

from .models import Documento, Temas, Usuario, Rol, Persona, Colegio, Administrador, Profesor, Curso

# ============================================================
# VISTAS PRINCIPALES DE GESTIÓN DE DOCUMENTOS
# ============================================================

def gestion_documentos_profesor(request):
    """Vista exclusiva para profesores para gestionar documentos"""
    documentos = Documento.objects.all().order_by('-fecha_creacion')
    
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return manejar_ajax_documentos(request)
    
    return render(request, 'profesor/gestion_documentos.html', {
        'documentos': documentos
    })

def gestion_documentos_administrador(request):
    """Vista específica para administradores"""
    print("📥 Llegó a gestion_documentos_administrador")
    
    try:
        documentos = Documento.objects.all().order_by('-fecha_creacion')
        
        if request.method == 'POST':
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return manejar_ajax_documentos(request)
        
        return render(request, 'administrador/gestion_documentos.html', {
            'documentos': documentos
        })
            
    except Exception as e:
        print(f"❌ Error en gestion_documentos_administrador: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)

def gestion_documentos_superadministrador(request):
    """Vista exclusiva para superadministradores para gestionar documentos"""
    documentos = Documento.objects.all().order_by('-fecha_creacion')
    
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return manejar_ajax_documentos(request)
    
    return render(request, 'superadministrador/gestion_documentos.html', {
        'documentos': documentos
    })

# ============================================================
# FUNCIONES AUXILIARES PARA CREAR ESTRUCTURA
# ============================================================

def crear_estructura_si_no_existe():
    """SOLUCIÓN CON MODELO TEMAS REAL"""
    try:
        # Verificar si ya existe un tema
        tema_existente = Temas.objects.first()
        if tema_existente:
            print("✅ Tema existente encontrado")
            return tema_existente
        
        print("🔧 Creando estructura con modelo Temas real...")
        
        # PASO 1: CREAR ROLES
        print("📋 Paso 1: Creando roles...")
        rol_admin, _ = Rol.objects.get_or_create(tipo='Administrador')
        rol_profesor, _ = Rol.objects.get_or_create(tipo='Profesor')
        print("✅ Roles creados")
        
        # PASO 2: CREAR USUARIOS
        print("📋 Paso 2: Creando usuarios...")
        
        usuario_admin, _ = Usuario.objects.get_or_create(
            correo='admin_sistema@temp.com',
            defaults={
                'rol': rol_admin,
                'contrasenia': make_password('admin123'),
                'estado': 'activo'
            }
        )
        
        usuario_profesor, _ = Usuario.objects.get_or_create(
            correo='profesor_sistema@temp.com', 
            defaults={
                'rol': rol_profesor,
                'contrasenia': make_password('prof123'),
                'estado': 'activo'
            }
        )
        print("✅ Usuarios creados")
        
        # PASO 3: CREAR PERSONAS
        print("📋 Paso 3: Creando personas...")
        
        persona_admin, _ = Persona.objects.get_or_create(
            usuario=usuario_admin,
            defaults={
                'nombre': 'Admin',
                'apellidoPaterno': 'Sistema',
                'apellidoMaterno': 'Temp',
                'estado': 'activo'
            }
        )
        
        persona_profesor, _ = Persona.objects.get_or_create(
            usuario=usuario_profesor,
            defaults={
                'nombre': 'Profesor',
                'apellidoPaterno': 'Temporal', 
                'apellidoMaterno': 'Sistema',
                'estado': 'activo'
            }
        )
        print("✅ Personas creadas")
        
        # PASO 4: CREAR COLEGIO
        print("📋 Paso 4: Creando colegio...")
        colegio_default, _ = Colegio.objects.get_or_create(
            nombre='Colegio Temporal Sistema',
            defaults={
                'direccion': 'Dirección temp 123',
                'estado': 'activo'
            }
        )
        print("✅ Colegio creado")
        
        # PASO 5: CREAR ADMINISTRADOR
        print("📋 Paso 5: Creando administrador...")
        admin_obj, _ = Administrador.objects.get_or_create(
            usuario=usuario_admin,
            defaults={'colegio': colegio_default}
        )
        print("✅ Administrador creado")
        
        # PASO 6: CREAR PROFESOR
        print("📋 Paso 6: Creando profesor...")
        profesor_default, _ = Profesor.objects.get_or_create(
            usuario=usuario_profesor,
            defaults={'colegio': colegio_default}
        )
        print("✅ Profesor creado")
        
        # PASO 7: CREAR CURSO
        print("📋 Paso 7: Creando curso...")
        curso_default, _ = Curso.objects.get_or_create(
            nombre='Física General - Temporal',
            defaults={'profesor': profesor_default}
        )
        print("✅ Curso creado")
        
        # PASO 8: CREAR TEMA - CON TUS CAMPOS REALES
        print("📋 Paso 8: Creando tema...")
        tema_default = Temas.objects.create(
            curso=curso_default,
            nombre_archivo='Física General y Conceptos Básicos',
            descripcion='Tema temporal para documentos del sistema de física',
            numero=1,
            estado='disponible',
            fecha_inicio=timezone.now().date(),
            tamanio=10,
            archivo=None
        )
        print(f"✅ TEMA CREADO EXITOSAMENTE: {tema_default.id}")
        
        return tema_default
        
    except Exception as e:
        print(f"❌ ERROR en crear_estructura_si_no_existe:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        import traceback
        print("   Traceback completo:")
        print(traceback.format_exc())
        return None

def crear_estructura_emergencia():
    """SOLUCIÓN DE EMERGENCIA CON MODELO TEMAS REAL"""
    try:
        tema_existente = Temas.objects.first()
        if tema_existente:
            return tema_existente
        
        print("🚨 CREANDO ESTRUCTURA DE EMERGENCIA...")
        
        # Buscar cualquier curso existente
        curso = Curso.objects.first()
        
        # Si no hay curso, crear uno mínimo
        if not curso:
            # Buscar cualquier profesor
            profesor = Profesor.objects.first()
            
            # Crear curso
            curso_data = {'nombre': "Curso Emergencia Física"}
            if profesor:
                curso_data['profesor'] = profesor
            curso = Curso.objects.create(**curso_data)
            print("✅ Curso de emergencia creado")
        
        # Crear tema con campos REALES de tu modelo
        tema_default = Temas.objects.create(
            curso=curso,
            nombre_archivo="Tema Emergencia Física General",
            descripcion="Tema temporal del sistema",
            numero=1,
            estado="disponible",
            fecha_inicio=timezone.now().date(),
            tamanio=1,
            archivo=None
        )
        print(f"✅ Tema de emergencia creado: {tema_default.id}")
        
        return tema_default
        
    except Exception as e:
        print(f"❌ FALLA en emergencia: {e}")
        return None

# ============================================================
# MANEJO DE PETICIONES AJAX
# ============================================================

@require_POST
@csrf_protect
def manejar_ajax_documentos(request):
    """Manejar operaciones AJAX para documentos"""
    if request.method == 'POST':
        try:
            print("📥 Datos recibidos en manejar_ajax_documentos")
            print("Content-Type:", request.content_type)
            print("POST data:", dict(request.POST))
            print("FILES data:", dict(request.FILES))
            
            # Verificar si es FormData (con archivos)
            if request.content_type.startswith('multipart/form-data'):
                action = request.POST.get('action', 'crear')
                
                if action == 'crear':
                    return crear_documento_con_archivos(request)
                elif action == 'editar':
                    return editar_documento_con_archivos(request)
                elif action == 'eliminar':
                    return eliminar_documento_ajax(request)
                else:
                    return JsonResponse({'error': 'Acción no válida'}, status=400)
                    
            else:
                # Manejo normal JSON (sin archivos)
                data = json.loads(request.body)
                action = data.get('action')
                
                if action == 'eliminar':
                    return eliminar_documento_ajax(data)
                else:
                    return JsonResponse({'error': 'Acción JSON no soportada para crear/editar'}, status=400)
                
        except Exception as e:
            print(f"❌ Error en manejar_ajax_documentos: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def crear_documento_con_archivos(request):
    """Crear documento con archivos - VERSIÓN FINAL"""
    try:
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '')
        estado = request.POST.get('estado', 'Activo')
        categoria = request.POST.get('categoria', 'fisica_general')
        
        print(f"📝 Creando documento: {nombre}")
        
        if not nombre:
            return JsonResponse({'error': 'El nombre es requerido'}, status=400)
        
        # INTENTAR CREAR ESTRUCTURA
        tema_default = crear_estructura_si_no_existe()
        
        if not tema_default:
            print("❌ Falló estructura principal, intentando emergencia...")
            tema_default = crear_estructura_emergencia()
        
        if not tema_default:
            return JsonResponse({
                'error': 'No se pudo configurar el sistema. Contacta al administrador.'
            }, status=400)
        
        # CREAR DOCUMENTO
        documento = Documento(
            nombre=nombre,
            descripcion=descripcion,
            estado=estado,
            categoria=categoria,
            tema=tema_default
        )
        
        # MANEJAR ARCHIVO PDF
        if 'archivo_pdf' in request.FILES:
            archivo = request.FILES['archivo_pdf']
            print(f"📎 Procesando archivo: {archivo.name}")
            
            if not archivo.name.lower().endswith('.pdf'):
                return JsonResponse({'error': 'Solo se permiten archivos PDF'}, status=400)
            
            if archivo.size > 10 * 1024 * 1024:
                return JsonResponse({'error': 'El archivo es demasiado grande (máx. 10MB)'}, status=400)
            
            documento.archivo_pdf = archivo
        
        # GUARDAR DOCUMENTO
        documento.save()
        print(f"🎉 DOCUMENTO CREADO EXITOSAMENTE: {documento.id}")
        
        return JsonResponse({
            'success': True,
            'message': 'Documento creado correctamente' + (' con PDF' if 'archivo_pdf' in request.FILES else '')
        })
        
    except Exception as e:
        print(f"❌ ERROR en crear_documento_con_archivos: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'error': f'Error al crear documento: {str(e)}'}, status=500)

def editar_documento_con_archivos(request):
    """Editar documento con archivos"""
    try:
        documento_id = request.POST.get('id')
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '')
        estado = request.POST.get('estado', 'Activo')
        categoria = request.POST.get('categoria', 'fisica_general')
        remove_current_file = request.POST.get('remove_current_file') == 'true'
        
        print(f"✏️ Editando documento ID: {documento_id}")
        
        if not documento_id:
            return JsonResponse({'error': 'ID de documento requerido'}, status=400)
        
        documento = Documento.objects.get(id=documento_id)
        documento.nombre = nombre
        documento.descripcion = descripcion
        documento.estado = estado
        documento.categoria = categoria
        
        # Si el documento no tiene tema, asignarle uno
        if not documento.tema:
            tema_default = crear_estructura_si_no_existe()
            if tema_default:
                documento.tema = tema_default
        
        # Manejar eliminación de archivo actual
        if remove_current_file:
            print("🗑️ Eliminando archivo actual")
            if documento.archivo_pdf:
                documento.archivo_pdf.delete(save=False)
            documento.archivo_pdf = None
        
        # Manejar nuevo archivo PDF
        if 'archivo_pdf' in request.FILES:
            archivo = request.FILES['archivo_pdf']
            print(f"📎 Nuevo archivo: {archivo.name}, tamaño: {archivo.size}")
            
            # Validaciones
            if not archivo.name.lower().endswith('.pdf'):
                return JsonResponse({'error': 'Solo se permiten archivos PDF'}, status=400)
            
            if archivo.size > 10 * 1024 * 1024:
                return JsonResponse({'error': 'El archivo es demasiado grande (máx. 10MB)'}, status=400)
            
            # Eliminar archivo anterior si existe
            if documento.archivo_pdf:
                documento.archivo_pdf.delete(save=False)
            
            documento.archivo_pdf = archivo
        
        documento.save()
        print(f"✅ Documento actualizado: {documento.id}")
        
        return JsonResponse({
            'success': True,
            'message': 'Documento actualizado correctamente' + (' con nuevo PDF' if 'archivo_pdf' in request.FILES else '')
        })
        
    except Documento.DoesNotExist:
        return JsonResponse({'error': 'Documento no encontrado'}, status=404)
    except Exception as e:
        print(f"❌ Error al editar documento: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'error': f'Error al editar documento: {str(e)}'}, status=500)

def eliminar_documento_ajax(data):
    """Eliminar documento via AJAX"""
    try:
        documento_id = data.get('id')
        if not documento_id:
            return JsonResponse({'error': 'ID de documento requerido'}, status=400)
        
        documento = Documento.objects.get(id=documento_id)
        documento_nombre = documento.nombre
        
        # Eliminar archivo físico si existe
        if documento.archivo_pdf:
            documento.archivo_pdf.delete(save=False)
            
        documento.delete()
        print(f"✅ Documento eliminado: {documento_nombre}")
        
        return JsonResponse({
            'success': True,
            'message': f'Documento "{documento_nombre}" eliminado correctamente'
        })
        
    except Documento.DoesNotExist:
        return JsonResponse({'error': 'Documento no encontrado'}, status=404)
    except Exception as e:
        print(f"❌ Error al eliminar documento: {str(e)}")
        return JsonResponse({'error': f'Error al eliminar documento: {str(e)}'}, status=500)

# ============================================================
# VISTAS PARA ESTUDIANTES (CONSULTA DE DOCUMENTOS)
# ============================================================

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

# ============================================================
# FUNCIONES OBSOLETAS (MANTENIDAS POR COMPATIBILIDAD)
# ============================================================

def crear_documento_ajax(request_or_data):
    """Función obsoleta - Mantenida por compatibilidad"""
    print("⚠️  Usando función obsoleta crear_documento_ajax")
    return crear_documento_con_archivos(request_or_data)
# =====================
# COMPONENTES EN TARJETAS PARA PROFESOR
# =====================
from django.core.serializers.json import DjangoJSONEncoder

def componentes_profesor_tarjetas(request):
    componentes = Componente.objects.all().select_related('laboratorio')
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
            # 'tema' eliminado, mantener campo vacío o derivado de otra entidad si es necesario
            'tema_nombre': '',
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
    componentes = Componente.objects.all().select_related('laboratorio')
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
            'tema_nombre': '',
            'laboratorio_nombre': c.laboratorio.nombre if c.laboratorio else '',
        })
    context = {
        'componentes': componentes,
        'componentes_json': json.dumps(componentes_json, cls=DjangoJSONEncoder)
    }
    return render(request, 'estudiante/componentes_tarjetas.html', context)


