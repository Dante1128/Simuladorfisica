from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from .models import Usuario  
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Laboratorio
from django.utils import timezone
from .models import Colegio
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
import csv
import json
from django.db import models
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q
import base64
from .models import Documento  
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
import json

def index(request):
    return render(request, 'paginaWeb/index.html')
def base_cliente(request):
    return render(request, 'cliente/baseCliente.html')

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

    # ELIMINAR COLEGIO
    eliminar_id = request.GET.get('eliminar')
    if eliminar_id:
        colegio = Colegio.objects.filter(id=eliminar_id).first()
        if colegio:
            colegio.delete()
            messages.success(request, 'Colegio eliminado correctamente.')
        else:
            messages.error(request, 'Colegio no encontrado.')

    # FILTRAR COLEGIOS
    filtro = request.GET.get('filtro', '').strip()
    if filtro:
        colegios = Colegio.objects.filter(
            Q(nombre__icontains=filtro) | Q(direccion__icontains=filtro)
        ).order_by('nombre')
    else:
        colegios = Colegio.objects.all().order_by('nombre')

    context = {
        'colegios': colegios,
    }
    return render(request, 'superadministrador/gestion_colegios.html', context)


def editar_colegio(request, colegio_id):
    """
    Vista para editar un colegio existente
    """
    try:
        colegio = get_object_or_404(Colegio, id=colegio_id)
        
        if request.method == 'GET':
            # Devolver datos del colegio para edición
            return JsonResponse({
                'success': True,
                'colegio': {
                    'id': colegio.id,
                    'nombre': colegio.nombre,
                    'direccion': colegio.direccion
                }
            })
        
        elif request.method == 'POST':
            # Actualizar el colegio
            data = json.loads(request.body)
            nombre = data.get('nombre', '').strip()
            direccion = data.get('direccion', '').strip()
            
            if not nombre or not direccion:
                return JsonResponse({
                    'success': False,
                    'message': 'Nombre y dirección son campos obligatorios'
                }, status=400)
            
            # Verificar si el nombre ya existe (excluyendo el actual)
            if Colegio.objects.filter(nombre__iexact=nombre).exclude(id=colegio_id).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Ya existe otro colegio con ese nombre'
                }, status=400)
            
            # Actualizar el colegio
            colegio.nombre = nombre
            colegio.direccion = direccion
            colegio.save()
            
            print(f"Colegio actualizado en usuarios_colegios: ID {colegio.id}")
            
            return JsonResponse({
                'success': True,
                'message': f'Colegio "{colegio.nombre}" actualizado correctamente',
                'colegio': {
                    'id': colegio.id,
                    'nombre': colegio.nombre,
                    'direccion': colegio.direccion
                }
            })
            
    except Exception as e:
        print(f"Error en editar_colegio: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}'
        }, status=500)


def eliminar_colegio(request, colegio_id):
    """
    Vista para eliminar un colegio
    """
    try:
        colegio = get_object_or_404(Colegio, id=colegio_id)
        nombre_colegio = colegio.nombre
        colegio.delete()
        
        print(f"Colegio eliminado de usuarios_colegios: ID {colegio_id}")
        
        return JsonResponse({
            'success': True,
            'message': f'Colegio "{nombre_colegio}" eliminado correctamente'
        })
        
    except Exception as e:
        print(f"Error en eliminar_colegio: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error al eliminar el colegio: {str(e)}'
        }, status=500)

def buscar_colegios(request):
    """
    Vista para búsqueda de colegios
    """
    try:
        query = request.GET.get('q', '').strip()
        
        if not query:
            colegios = Colegio.objects.all().order_by('nombre')
        else:
            colegios = Colegio.objects.filter(
                Q(nombre__icontains=query) |
                Q(direccion__icontains=query)
            ).order_by('nombre')
        
        colegios_data = []
        for colegio in colegios:
            colegios_data.append({
                'id': colegio.id,
                'nombre': colegio.nombre,
                'direccion': colegio.direccion
            })
        
        return JsonResponse({
            'success': True,
            'colegios': colegios_data
        })
    
    except Exception as e:
        print(f"Error en buscar_colegios: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error en la búsqueda: {str(e)}'
        }, status=500)

def exportar_colegios(request):
    """
    Vista para exportar la lista de colegios a CSV
    """
    try:
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="colegios.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Nombre', 'Dirección'])
        
        colegios = Colegio.objects.all().order_by('nombre')
        for colegio in colegios:
            writer.writerow([
                colegio.id, 
                colegio.nombre, 
                colegio.direccion
            ])
        
        return response
    
    except Exception as e:
        print(f"Error en exportar_colegios: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error al exportar: {str(e)}'
        })
    
def gestion_cursos(request):
    """Vista básica para base de administración"""
    return render(request, 'superadministrador/gestion_cursos.html')

def gestion_estudiante(request):
    """Vista básica para base de administración"""
    return render(request, 'superadministrador/gestion_estudiante.html')
#estudiante
def panel_estudiante(request):
    """Vista básica para panel de administración"""
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return render(request, 'estudiante/panel_estudiante.html', {"usuario": None})
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        return render(request, 'estudiante/panel_estudiante.html', {"usuario": None})
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
    #====================================================================
# CRUD PROFESORES
#====================================================================
from .models import Profesor, Colegio, Usuario

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
                usuario = Usuario.objects.create(
                    correo=correo,
                    contrasenia=contrasenia,
                    estado='A',
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

    # ELIMINAR PROFESOR
    eliminar_id = request.GET.get('eliminar')
    if eliminar_id:
        profesor = Profesor.objects.filter(id=eliminar_id).first()
        if profesor:
            profesor.usuario.delete()
            profesor.delete()
            messages.success(request, 'Profesor eliminado correctamente.')
        else:
            messages.error(request, 'Profesor no encontrado.')

    # LISTAR PROFESORES
    profesores = Profesor.objects.select_related('usuario', 'colegio').all().order_by('usuario__correo')
    colegios = Colegio.objects.all().order_by('nombre')
    context = {
        'profesores': profesores,
        'colegios': colegios,
    }
    return render(request, 'superadministrador/gestion_profesor.html', context)

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
#===========================================
#LOGIN
#====================================================================
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
        if usuario.rol and usuario.rol.tipo:
            rol_lower = usuario.rol.tipo.lower()
                
            if rol_lower == 'superadministrador':
                return redirect('panel_superadmin')
            elif rol_lower == 'administrador':
                return redirect('panel_admin')
            elif rol_lower == 'profesor':
                return redirect('panel_profesor')
            else:
                return redirect('panel_estudiante')
        else:
            messages.error(request, 'El usuario no tiene rol asignado.')
            return render(request, 'registration/login.html')
        
    # ⚠️ Muy importante: SIEMPRE retornar algo si no es POST
    return render(request, 'registration/login.html')

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
    
