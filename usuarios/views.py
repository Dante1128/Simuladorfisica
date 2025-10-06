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

def gestion_usuarios(request):
    """Vista básica para gestión de usuarios"""
    usuarios = Usuario.objects.all()
    return render(request, 'administrador/gestion_usuarios.html', {"usuarios": usuarios})

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

# ============ VISTAS PARA REPORTES COMPLETAMENTE CORREGIDAS ============

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.utils.timezone import now, timedelta, make_aware
from django.db import models
from .models import Usuario, Membresia, Laboratorio, ActividadSimulacion, Pago
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io
from datetime import datetime

# DASHBOARD PRINCIPAL DE REPORTES CON FILTROS MANIPULABLES
def dashboard_reportes(request):
    """Vista principal del dashboard de reportes con filtros interactivos"""
    
    # OBTENER PARÁMETROS DE FILTRO DEL FORMULARIO
    periodo = request.GET.get('periodo', 'mes')  # dia, semana, mes, año, personalizado
    fecha_inicio_str = request.GET.get('fecha_inicio', '')
    fecha_fin_str = request.GET.get('fecha_fin', '')
    
    # Calcular fechas según el período seleccionado (usando timezone-aware)
    if periodo == 'dia':
        fecha_fin = now().date()
        fecha_inicio = fecha_fin
    elif periodo == 'semana':
        fecha_fin = now().date()
        fecha_inicio = fecha_fin - timedelta(days=7)
    elif periodo == 'mes':
        fecha_fin = now().date()
        fecha_inicio = fecha_fin - timedelta(days=30)
    elif periodo == 'año':
        fecha_fin = now().date()
        fecha_inicio = fecha_fin.replace(month=1, day=1)
    elif periodo == 'personalizado' and fecha_inicio_str and fecha_fin_str:
        # Filtro personalizado por fechas específicas
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            # Si hay error, usar mes actual por defecto
            fecha_fin = now().date()
            fecha_inicio = fecha_fin - timedelta(days=30)
            periodo = 'mes'
    else:
        # Por defecto: último mes
        fecha_fin = now().date()
        fecha_inicio = fecha_fin - timedelta(days=30)
        periodo = 'mes'
    
    # CORREGIDO: Usar campos existentes del modelo Usuario
    total_usuarios = Usuario.objects.count()
    usuarios_activos = total_usuarios  # Todos los usuarios se consideran activos
    
    # Simulaciones realizadas en el período seleccionado (CORREGIDO: usar timezone-aware)
    simulaciones_realizadas = ActividadSimulacion.objects.filter(
        fecha_actividad__date__range=[fecha_inicio, fecha_fin]
    ).count()
    
    # Ingresos del período seleccionado
    ingresos_periodo = Pago.objects.filter(
        fecha_pago__date__range=[fecha_inicio, fecha_fin]
    ).aggregate(total=models.Sum('monto'))['total'] or 0
    
    # Comparacion con período anterior (misma duración)
    dias_periodo = (fecha_fin - fecha_inicio).days
    fecha_inicio_anterior = fecha_inicio - timedelta(days=dias_periodo + 1)
    fecha_fin_anterior = fecha_inicio - timedelta(days=1)
    
    simulaciones_anterior = ActividadSimulacion.objects.filter(
        fecha_actividad__date__range=[fecha_inicio_anterior, fecha_fin_anterior]
    ).count()
    
    # Para usuarios, como no tenemos fecha_registro, contamos todos los usuarios existentes
    usuarios_activos_anterior = Usuario.objects.count()
    
    # Calcular porcentajes
    porcentaje_simulaciones = calcular_porcentaje(simulaciones_realizadas, simulaciones_anterior)
    porcentaje_usuarios = calcular_porcentaje(usuarios_activos, usuarios_activos_anterior)
    
    # Estadisticas por tipo de usuario - SIN FILTRO POR FECHA (no hay fecha_registro)
    usuarios_por_tipo_data = {
        'estudiante': Usuario.objects.filter(tipo='estudiante').count(),
        'universitario': Usuario.objects.filter(tipo='universitario').count(),
        'profesional': Usuario.objects.filter(tipo='profesional').count(),
    }
    
    # CALCULAR PORCENTAJES PARA GRAFICO DE PASTEL
    total_usuarios_tipo = sum(usuarios_por_tipo_data.values()) or 1
    usuarios_por_tipo = {}
    
    for tipo, cantidad in usuarios_por_tipo_data.items():
        porcentaje = round((cantidad / total_usuarios_tipo) * 100, 1)
        usuarios_por_tipo[tipo] = cantidad
        usuarios_por_tipo[f'{tipo}_porc'] = porcentaje
    
    # Estadisticas de membresias
    membresias_por_tipo = {
        'mensual': Membresia.objects.filter(tipo_membresia='mensual', estado='activo').count(),
        'semestral': Membresia.objects.filter(tipo_membresia='semestral', estado='activo').count(),
        'anual': Membresia.objects.filter(tipo_membresia='anual', estado='activo').count(),
    }
    
    total_membresias_grafico = sum(membresias_por_tipo.values()) or 1
    
    # Datos para grafico de lineas (según el período seleccionado) - CORREGIDO: usar timezone-aware
    meses_actividad = []
    max_simulaciones_mes = 1
    
    # Ajustar el gráfico según el período seleccionado
    if periodo == 'dia':
        # Gráfico por horas del día seleccionado - CORREGIDO: usar make_aware para timezone
        for hora in range(0, 24):
            # Crear datetime con timezone
            hora_inicio = make_aware(datetime(fecha_inicio.year, fecha_inicio.month, fecha_inicio.day, hora, 0, 0))
            hora_fin = hora_inicio + timedelta(hours=1)
            
            simulaciones_hora = ActividadSimulacion.objects.filter(
                fecha_actividad__range=[hora_inicio, hora_fin]
            ).count()
            
            meses_actividad.append({
                'mes': f"{hora:02d}:00",
                'simulaciones': simulaciones_hora
            })
            
            if simulaciones_hora > max_simulaciones_mes:
                max_simulaciones_mes = simulaciones_hora
                
    elif periodo == 'semana':
        # Gráfico por días de la semana
        for i in range(7):
            dia = fecha_inicio + timedelta(days=i)
            simulaciones_dia = ActividadSimulacion.objects.filter(
                fecha_actividad__date=dia
            ).count()
            
            meses_actividad.append({
                'mes': dia.strftime('%a'),
                'simulaciones': simulaciones_dia
            })
            
            if simulaciones_dia > max_simulaciones_mes:
                max_simulaciones_mes = simulaciones_dia
                
    else:
        # Gráfico por meses (comportamiento original para mes, año y personalizado)
        meses_grafico = 6 if periodo == 'mes' else 12
        
        for i in range(meses_grafico - 1, -1, -1):
            mes_fin = fecha_fin.replace(day=1) - timedelta(days=30*i)
            mes_inicio = mes_fin.replace(day=1)
            mes_siguiente = (mes_fin + timedelta(days=32)).replace(day=1)
            
            simulaciones_mes = ActividadSimulacion.objects.filter(
                fecha_actividad__date__range=[mes_inicio, mes_siguiente - timedelta(days=1)]
            ).count()
            
            meses_actividad.append({
                'mes': mes_inicio.strftime('%b %Y'),
                'simulaciones': simulaciones_mes
            })
            
            if simulaciones_mes > max_simulaciones_mes:
                max_simulaciones_mes = simulaciones_mes
    
    context = {
        # Metricas principales
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'simulaciones_realizadas': simulaciones_realizadas,
        'ingresos_periodo': ingresos_periodo,
        'porcentaje_simulaciones': porcentaje_simulaciones,
        'porcentaje_usuarios': porcentaje_usuarios,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        
        # PARÁMETROS DE FILTRO ACTUALES
        'periodo_seleccionado': periodo,
        'fecha_inicio_str': fecha_inicio_str or fecha_inicio.isoformat(),
        'fecha_fin_str': fecha_fin_str or fecha_fin.isoformat(),
        
        # SOLO DATOS PARA GRÁFICOS - NO TABLAS DETALLADAS EN DASHBOARD
        'usuarios_por_tipo': usuarios_por_tipo,
        'membresias_por_tipo': membresias_por_tipo,
        'total_membresias_grafico': total_membresias_grafico,
        'meses_actividad': meses_actividad,
        'max_simulaciones_mes': max_simulaciones_mes,
    }
    
    return render(request, 'informes-reportes/dashboard_reportes.html', context)

def calcular_porcentaje(actual, anterior):
    """Calcular porcentaje de crecimiento"""
    if anterior == 0:
        return 0
    return round(((actual - anterior) / anterior) * 100, 1)

# PDF UNIFICADO COMPLETO - SIEMPRE MOSTRAR TODAS LAS TABLAS (INCLUSO VACÍAS)
def generar_informe_completo_pdf(request):
    """Generar PDF unificado mostrando TODAS las tablas siempre"""

    # Obtener parámetros de filtro si existen
    periodo = request.GET.get('periodo', '')
    fecha_inicio_str = request.GET.get('fecha_inicio', '')
    fecha_fin_str = request.GET.get('fecha_fin', '')
    
    # Crear el objeto PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    table_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica')
    ])

    # Título del informe
    titulo = "INFORME COMPLETO - SISTEMA DE LABORATORIOS VR"
    if fecha_inicio_str and fecha_fin_str:
        titulo = f"INFORME COMPLETO - {fecha_inicio_str} a {fecha_fin_str}"
    
    elements.append(Paragraph(titulo, title_style))
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # ==================== TABLA DE ESTUDIANTES ====================
    estudiantes = Usuario.objects.filter(tipo='estudiante').order_by('nombre')
    data_estudiantes = [['#', 'Nombre', 'Correo']]
    
    if estudiantes.exists():
        for i, estudiante in enumerate(estudiantes, 1):
            data_estudiantes.append([i, estudiante.nombre, estudiante.correo])
    else:
        data_estudiantes.append(['-', 'No hay estudiantes registrados', '-'])
    
    table_estudiantes = Table(data_estudiantes, hAlign='LEFT')
    table_estudiantes.setStyle(table_style)
    elements.append(Paragraph("ESTUDIANTES REGISTRADOS", styles['Heading2']))
    elements.append(Paragraph("<br/>", styles['Normal']))
    elements.append(table_estudiantes)
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # ==================== TABLA DE PROFESIONALES ====================
    profesionales = Usuario.objects.filter(tipo='profesional').order_by('nombre')
    data_profesionales = [['#', 'Nombre', 'Correo']]
    
    if profesionales.exists():
        for i, profesional in enumerate(profesionales, 1):
            data_profesionales.append([i, profesional.nombre, profesional.correo])
    else:
        data_profesionales.append(['-', 'No hay profesionales registrados', '-'])
    
    table_profesionales = Table(data_profesionales, hAlign='LEFT')
    table_profesionales.setStyle(table_style)
    elements.append(Paragraph("PROFESIONALES REGISTRADOS", styles['Heading2']))
    elements.append(Paragraph("<br/>", styles['Normal']))
    elements.append(table_profesionales)
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # ==================== TABLA DE UNIVERSITARIOS ====================
    universitarios = Usuario.objects.filter(tipo='universitario').order_by('nombre')
    data_universitarios = [['#', 'Nombre', 'Correo']]
    
    if universitarios.exists():
        for i, universitario in enumerate(universitarios, 1):
            data_universitarios.append([i, universitario.nombre, universitario.correo])
    else:
        data_universitarios.append(['-', 'No hay universitarios registrados', '-'])
    
    table_universitarios = Table(data_universitarios, hAlign='LEFT')
    table_universitarios.setStyle(table_style)
    elements.append(Paragraph("UNIVERSITARIOS REGISTRADOS", styles['Heading2']))
    elements.append(Paragraph("<br/>", styles['Normal']))
    elements.append(table_universitarios)
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # ==================== TABLA DE MEMBRESIAS ====================
    try:
        membresias = Membresia.objects.select_related('usuario').all()
        data_membresias = [['#', 'Usuario', 'Tipo Membresía', 'Estado']]
        
        if membresias.exists():
            for i, membresia in enumerate(membresias, 1):
                data_membresias.append([i, membresia.usuario.nombre, membresia.tipo_membresia, membresia.estado])
        else:
            data_membresias.append(['-', 'No hay membresías', '-', '-'])
        
        table_membresias = Table(data_membresias, hAlign='LEFT')
        table_membresias.setStyle(table_style)
        elements.append(Paragraph("MEMBRESÍAS DEL SISTEMA", styles['Heading2']))
        elements.append(Paragraph("<br/>", styles['Normal']))
        elements.append(table_membresias)
        elements.append(Paragraph("<br/><br/>", styles['Normal']))
    except Exception as e:
        data_membresias = [['#', 'Usuario', 'Tipo Membresía', 'Estado'], ['-', f'Error: {str(e)}', '-', '-']]
        table_membresias = Table(data_membresias, hAlign='LEFT')
        table_membresias.setStyle(table_style)
        elements.append(Paragraph("MEMBRESÍAS DEL SISTEMA", styles['Heading2']))
        elements.append(Paragraph("<br/>", styles['Normal']))
        elements.append(table_membresias)
        elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # ==================== TABLA DE ACTIVIDADES ====================
    try:
        actividades = ActividadSimulacion.objects.select_related('usuario', 'laboratorio').all()
        data_actividades = [['#', 'Usuario', 'Laboratorio', 'Fecha']]
        
        if actividades.exists():
            for i, actividad in enumerate(actividades, 1):
                data_actividades.append([i, actividad.usuario.nombre, actividad.laboratorio.nombre, actividad.fecha_actividad.strftime('%Y-%m-%d %H:%M')])
        else:
            data_actividades.append(['-', 'No hay actividades', '-', '-'])
        
        table_actividades = Table(data_actividades, hAlign='LEFT')
        table_actividades.setStyle(table_style)
        elements.append(Paragraph("ACTIVIDADES DE SIMULACIÓN", styles['Heading2']))
        elements.append(Paragraph("<br/>", styles['Normal']))
        elements.append(table_actividades)
        elements.append(Paragraph("<br/><br/>", styles['Normal']))
    except Exception as e:
        data_actividades = [['#', 'Usuario', 'Laboratorio', 'Fecha'], ['-', f'Error: {str(e)}', '-', '-']]
        table_actividades = Table(data_actividades, hAlign='LEFT')
        table_actividades.setStyle(table_style)
        elements.append(Paragraph("ACTIVIDADES DE SIMULACIÓN", styles['Heading2']))
        elements.append(Paragraph("<br/>", styles['Normal']))
        elements.append(table_actividades)
        elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # ==================== TABLA DE PAGOS ====================
    try:
        pagos = Pago.objects.select_related('usuario').all()
        data_pagos = [['#', 'Usuario', 'Monto', 'Fecha Pago']]
        
        if pagos.exists():
            for i, pago in enumerate(pagos, 1):
                data_pagos.append([i, pago.usuario.nombre, f"${pago.monto:.2f}", pago.fecha_pago.strftime('%Y-%m-%d')])
        else:
            data_pagos.append(['-', 'No hay pagos', '$0.00', '-'])
        
        table_pagos = Table(data_pagos, hAlign='LEFT')
        table_pagos.setStyle(table_style)
        elements.append(Paragraph("PAGOS REALIZADOS", styles['Heading2']))
        elements.append(Paragraph("<br/>", styles['Normal']))
        elements.append(table_pagos)
    except Exception as e:
        data_pagos = [['#', 'Usuario', 'Monto', 'Fecha Pago'], ['-', f'Error: {str(e)}', '$0.00', '-']]
        table_pagos = Table(data_pagos, hAlign='LEFT')
        table_pagos.setStyle(table_style)
        elements.append(Paragraph("PAGOS REALIZADOS", styles['Heading2']))
        elements.append(Paragraph("<br/>", styles['Normal']))
        elements.append(table_pagos)

    # Generar PDF
    doc.build(elements)

    buffer.seek(0)
    filename = "informe_completo.pdf"
    if fecha_inicio_str and fecha_fin_str:
        filename = f"informe_{fecha_inicio_str}_a_{fecha_fin_str}.pdf"
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

# API PARA GRAFICOS (OPCIONAL)
def api_estadisticas(request):
    """API para obtener datos en tiempo real para graficos"""
    
    datos = {
        'usuarios_por_tipo': {
            'estudiante': Usuario.objects.filter(tipo='estudiante').count(),
            'universitario': Usuario.objects.filter(tipo='universitario').count(),
            'profesional': Usuario.objects.filter(tipo='profesional').count(),
        },
        'membresias_por_tipo': {
            'mensual': Membresia.objects.filter(tipo_membresia='mensual', estado='activo').count(),
            'anual': Membresia.objects.filter(tipo_membresia='anual', estado='activo').count(),
        }
    }
    
    return JsonResponse(datos)

from .models import Documento  
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
import json

# Cambiar esta función:
 
def gestion_documentos(request):
    """
    Vista exclusiva para administradores para gestionar documentos
    """
    documentos = Documento.objects.all().order_by('-fecha_creacion')
    
    if request.method == 'POST':
        # Manejar AJAX requests para crear/editar/eliminar
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return manejar_ajax_documentos(request)
    
    return render(request, 'temas/gestion_documentos.html', {
        'documentos': documentos
    })

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
                    return crear_documento_ajax_simple(data)
                elif action == 'editar':
                    return editar_documento_ajax(data)
                elif action == 'eliminar':
                    return eliminar_documento_ajax(data)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)
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
    
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q
import base64

# ... tus otras funciones existentes ...

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
    return render(request, 'temas/contenido_temas.html', context)

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
    



# ============ VISTAS PARA GESTIÓN DE USUARIOS ============

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from .models import Usuario
import json


def gestion_usuarios(request):
    """
    Vista principal para gestión de usuarios
    """
    usuarios = Usuario.objects.all().order_by('-id')
    
    # Manejar acciones del formulario
    if request.method == 'POST':
        action = request.POST.get('action')
        
        print(f"Acción recibida: {action}")  # Debug
        print(f"Datos POST: {request.POST}")  # Debug
        
        if action == 'crear':
            return crear_usuario(request)
        elif action == 'editar':
            return editar_usuario(request)
        elif action == 'eliminar':
            return eliminar_usuario(request)
    
    return render(request, 'administrador/gestion_usuarios.html', {
        'usuarios': usuarios
    })

def crear_usuario(request):
    """Crear nuevo usuario"""
    try:
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        correo = request.POST.get('correo', '').strip()
        tipo = request.POST.get('tipo', 'estudiante')
        contrasena = request.POST.get('contrasena', '').strip()
        
        print(f"Intentando crear usuario: {nombre} {apellido}, {correo}")  # Debug
        
        # Validaciones
        if not all([nombre, apellido, correo, contrasena]):
            return JsonResponse({
                'success': False, 
                'error': 'Todos los campos son obligatorios'
            })
        
        # Verificar si el correo ya existe
        if Usuario.objects.filter(correo=correo).exists():
            return JsonResponse({
                'success': False, 
                'error': 'El correo electrónico ya está registrado'
            })
        
        # Crear usuario
        usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            tipo=tipo,
            contrasena=make_password(contrasena)
        )
        usuario.save()
        
        print(f"Usuario creado exitosamente: {usuario.id}")  # Debug
        
        return JsonResponse({
            'success': True, 
            'message': 'Usuario creado correctamente',
            'user_id': usuario.id
        })
        
    except IntegrityError as e:
        print(f"Error de integridad: {e}")  # Debug
        return JsonResponse({
            'success': False, 
            'error': 'Error de base de datos: El correo ya existe'
        })
    except Exception as e:
        print(f"Error general: {e}")  # Debug
        return JsonResponse({
            'success': False, 
            'error': f'Error al crear usuario: {str(e)}'
        })

def editar_usuario(request):
    """Editar usuario existente"""
    try:
        user_id = request.POST.get('user_id')
        if not user_id:
            return JsonResponse({
                'success': False, 
                'error': 'ID de usuario requerido'
            })
        
        usuario = Usuario.objects.get(id=user_id)
        
        print(f"Editando usuario: {usuario.nombre} {usuario.apellido}")  # Debug
        
        # Actualizar campos
        usuario.nombre = request.POST.get('nombre', usuario.nombre).strip()
        usuario.apellido = request.POST.get('apellido', usuario.apellido).strip()
        usuario.correo = request.POST.get('correo', usuario.correo).strip()
        usuario.tipo = request.POST.get('tipo', usuario.tipo)
        
        # Si se proporciona nueva contraseña, actualizarla
        nueva_contrasena = request.POST.get('contrasena', '').strip()
        if nueva_contrasena:
            usuario.contrasena = make_password(nueva_contrasena)
        
        usuario.save()
        
        print(f"Usuario editado exitosamente: {usuario.id}")  # Debug
        
        return JsonResponse({
            'success': True,
            'message': 'Usuario actualizado correctamente'
        })
        
    except Usuario.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'error': 'Usuario no encontrado'
        })
    except Exception as e:
        print(f"Error al editar: {e}")  # Debug
        return JsonResponse({
            'success': False, 
            'error': f'Error al editar usuario: {str(e)}'
        })

def eliminar_usuario(request):
    """Eliminar usuario"""
    try:
        user_id = request.POST.get('id')
        if not user_id:
            return JsonResponse({
                'success': False, 
                'error': 'ID de usuario requerido'
            })
        
        usuario = Usuario.objects.get(id=user_id)
        usuario_nombre = f"{usuario.nombre} {usuario.apellido}"
        usuario.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Usuario "{usuario_nombre}" eliminado correctamente'
        })
        
    except Usuario.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'error': 'Usuario no encontrado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Laboratorio
from django.utils import timezone

def crear_laboratorio(request):
    if request.method == 'POST':
        nombre_simulacion = request.POST.get('nombre_simulacion')
        descripcion = request.POST.get('descripcion')
        estado = request.POST.get('estado', 'activo')
        archivo_laboratorio = request.FILES.get('archivo_laboratorio')

        laboratorio = Laboratorio(
            nombre_simulacion=nombre_simulacion,
            descripcion=descripcion,
            estado=estado,
            fecha_creacion=timezone.now(),
            archivo_laboratorio=archivo_laboratorio
        )
        laboratorio.save()
        messages.success(request, 'Laboratorio creado exitosamente.')
        return redirect('panel_admin')
    return render(request, 'laboratorios/crear_laboratorio.html')