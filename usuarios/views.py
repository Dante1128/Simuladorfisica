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

# ============ VISTAS PARA REPORTES CORREGIDAS ============

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
    
    # DATOS ADICIONALES - SIN FILTRAR POR FECHA DE REGISTRO (porque no existe el campo)
    usuarios = Usuario.objects.all().order_by('-id')[:10]
    
    # Para membresías, usar fecha_inicio si existe, sino mostrar todas
    try:
        # Intentar filtrar por fecha_inicio si el campo existe
        membresias = Membresia.objects.select_related('usuario').filter(
            estado='activo'
        )[:10]
    except:
        # Si no existe fecha_inicio, mostrar todas
        membresias = Membresia.objects.select_related('usuario').filter(
            estado='activo'
        )[:10]
    
    laboratorios = Laboratorio.objects.all()
    
    # Actividades SÍ pueden filtrarse por fecha_actividad (CORREGIDO: usar timezone-aware)
    actividades_recientes = ActividadSimulacion.objects.select_related(
        'usuario', 'laboratorio'
    ).filter(
        fecha_actividad__date__range=[fecha_inicio, fecha_fin]
    ).order_by('-fecha_actividad')[:10]
    
    # Pagos SÍ pueden filtrarse por fecha_pago
    pagos_recientes = Pago.objects.select_related('usuario').filter(
        fecha_pago__date__range=[fecha_inicio, fecha_fin]
    ).order_by('-fecha_pago')[:10]
    
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
    
    # Estadisticas de membresias - intentar filtrar por fecha si existe
    try:
        membresias_por_tipo = {
            'mensual': Membresia.objects.filter(
                tipo_membresia='mensual', 
                estado='activo'
            ).count(),
            'semestral': Membresia.objects.filter(
                tipo_membresia='semestral', 
                estado='activo'
            ).count(),
            'anual': Membresia.objects.filter(
                tipo_membresia='anual', 
                estado='activo'
            ).count(),
        }
    except:
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
        
        # DATOS UNIFICADOS
        'usuarios': usuarios,
        'membresias': membresias,
        'laboratorios': laboratorios,
        'actividades_recientes': actividades_recientes,
        'pagos_recientes': pagos_recientes,
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

# PDF UNIFICADO CORREGIDO (SIN FILTROS POR FECHA DE REGISTRO)
def generar_informe_completo_pdf(request):
    """Generar PDF unificado con todos los reportes, mostrando tablas aunque estén vacías"""

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
    if periodo and fecha_inicio_str and fecha_fin_str:
        titulo = f"INFORME COMPLETO - {fecha_inicio_str} a {fecha_fin_str}"
    
    elements.append(Paragraph(titulo, title_style))
    elements.append(Paragraph("<br/>", styles['Normal']))  # espacio

    # ==================== TABLA DE USUARIOS ====================
    usuarios = Usuario.objects.all().order_by('-id')
    data_usuarios = [['ID', 'Nombre', 'Correo', 'Tipo']]  # encabezados
    for u in usuarios:
        data_usuarios.append([u.id, u.nombre, u.correo, u.tipo])
    table_usuarios = Table(data_usuarios, hAlign='LEFT')
    table_usuarios.setStyle(table_style)
    elements.append(Paragraph("Usuarios Registrados", styles['Heading2']))
    elements.append(table_usuarios)
    elements.append(Paragraph("<br/>", styles['Normal']))  # espacio

    # ==================== TABLA DE MEMBRESIAS ====================
    membresias = Membresia.objects.select_related('usuario').all()
    data_membresias = [['ID', 'Usuario', 'Tipo Membresía', 'Estado']]
    for m in membresias:
        data_membresias.append([m.id, m.usuario.nombre, m.tipo_membresia, m.estado])
    table_membresias = Table(data_membresias, hAlign='LEFT')
    table_membresias.setStyle(table_style)
    elements.append(Paragraph("Membresías", styles['Heading2']))
    elements.append(table_membresias)
    elements.append(Paragraph("<br/>", styles['Normal']))

    # ==================== TABLA DE ACTIVIDADES (CON FILTRO SI EXISTE) ====================
    actividades = ActividadSimulacion.objects.select_related('usuario', 'laboratorio')
    
    # Aplicar filtro de fecha si se proporciona (CORREGIDO: usar timezone-aware)
    if fecha_inicio_str and fecha_fin_str:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            actividades = actividades.filter(
                fecha_actividad__date__range=[fecha_inicio, fecha_fin]
            )
        except (ValueError, TypeError):
            pass
    
    data_actividades = [['ID', 'Usuario', 'Laboratorio', 'Fecha']]
    for a in actividades:
        data_actividades.append([a.id, a.usuario.nombre, a.laboratorio.nombre, a.fecha_actividad.strftime('%Y-%m-%d')])
    table_actividades = Table(data_actividades, hAlign='LEFT')
    table_actividades.setStyle(table_style)
    elements.append(Paragraph("Actividades de Simulación", styles['Heading2']))
    elements.append(table_actividades)
    elements.append(Paragraph("<br/>", styles['Normal']))

    # ==================== TABLA DE PAGOS (CON FILTRO SI EXISTE) ====================
    pagos = Pago.objects.select_related('usuario')
    
    # Aplicar filtro de fecha si se proporciona
    if fecha_inicio_str and fecha_fin_str:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            pagos = pagos.filter(
                fecha_pago__date__range=[fecha_inicio, fecha_fin]
            )
        except (ValueError, TypeError):
            pass
    
    data_pagos = [['ID', 'Usuario', 'Monto', 'Fecha Pago']]
    for p in pagos:
        data_pagos.append([p.id, p.usuario.nombre, f"${p.monto:.2f}", p.fecha_pago.strftime('%Y-%m-%d')])
    table_pagos = Table(data_pagos, hAlign='LEFT')
    table_pagos.setStyle(table_style)
    elements.append(Paragraph("Pagos Realizados", styles['Heading2']))
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