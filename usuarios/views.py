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
    
    return render(request, 'contenidoTemas/gestion_documentos.html', {
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
    return render(request, 'contenidoTemas/contenido_temas.html', context)

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
    
