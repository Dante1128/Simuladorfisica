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

# ============ VISTAS PARA REPORTES ============

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.utils.timezone import now, timedelta
from django.db import models
from .models import Usuario, Membresia, Laboratorio, ActividadSimulacion, Pago
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io

# DASHBOARD PRINCIPAL DE REPORTES
def dashboard_reportes(request):
    """Vista principal del dashboard de reportes en tiempo real"""
    
    # Fechas para filtros (ultimos 30 dias)
    fecha_fin = now().date()
    fecha_inicio = fecha_fin - timedelta(days=30)
    
    # CORREGIDO: Tu modelo Usuario NO tiene campo 'estado'
    total_usuarios = Usuario.objects.count()
    usuarios_activos = total_usuarios  # Todos los usuarios se consideran activos
    
    # Simulaciones realizadas en el ultimo mes
    simulaciones_realizadas = ActividadSimulacion.objects.filter(
        fecha_actividad__date__range=[fecha_inicio, fecha_fin]
    ).count()
    
    # Ingresos del ultimo mes
    ingresos_mes = Pago.objects.filter(
        fecha_pago__date__range=[fecha_inicio, fecha_fin]
    ).aggregate(total=models.Sum('monto'))['total'] or 0
    
    # Comparacion con mes anterior
    fecha_inicio_anterior = fecha_inicio - timedelta(days=30)
    fecha_fin_anterior = fecha_inicio - timedelta(days=1)
    
    simulaciones_anterior = ActividadSimulacion.objects.filter(
        fecha_actividad__date__range=[fecha_inicio_anterior, fecha_fin_anterior]
    ).count()
    
    usuarios_activos_anterior = Usuario.objects.count()
    
    # Calcular porcentajes
    porcentaje_simulaciones = calcular_porcentaje(simulaciones_realizadas, simulaciones_anterior)
    porcentaje_usuarios = calcular_porcentaje(usuarios_activos, usuarios_activos_anterior)
    
    # DATOS ADICIONALES
    usuarios = Usuario.objects.all().order_by('-id')[:10]  # Ultimos 10 usuarios
    membresias = Membresia.objects.select_related('usuario').filter(estado='activo')[:10]
    laboratorios = Laboratorio.objects.all()
    actividades_recientes = ActividadSimulacion.objects.select_related('usuario', 'laboratorio').order_by('-fecha_actividad')[:10]
    pagos_recientes = Pago.objects.select_related('usuario').order_by('-fecha_pago')[:10]
    
    # Estadisticas por tipo de usuario CON PORCENTAJES
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
    
    # Datos para grafico de lineas (ultimos 6 meses)
    meses_actividad = []
    max_simulaciones_mes = 1
    
    for i in range(5, -1, -1):  # Ultimos 6 meses
        mes_fin = fecha_fin.replace(day=1) - timedelta(days=30*i)
        mes_inicio = mes_fin.replace(day=1)
        mes_siguiente = (mes_fin + timedelta(days=32)).replace(day=1)
        
        simulaciones_mes = ActividadSimulacion.objects.filter(
            fecha_actividad__date__range=[mes_inicio, mes_siguiente - timedelta(days=1)]
        ).count()
        
        meses_actividad.append({
            'mes': mes_inicio.strftime('%b'),
            'simulaciones': simulaciones_mes
        })
        
        if simulaciones_mes > max_simulaciones_mes:
            max_simulaciones_mes = simulaciones_mes
    
    context = {
        # Metricas principales
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'simulaciones_realizadas': simulaciones_realizadas,
        'ingresos_mes': ingresos_mes,
        'porcentaje_simulaciones': porcentaje_simulaciones,
        'porcentaje_usuarios': porcentaje_usuarios,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        
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

# PDF UNIFICADO CORREGIDO
def generar_informe_completo_pdf(request):
    """Generar PDF unificado con todos los reportes, mostrando tablas aunque estén vacías"""

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
    elements.append(Paragraph("INFORME COMPLETO - SISTEMA DE LABORATORIOS VR", title_style))
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

    # ==================== TABLA DE ACTIVIDADES ====================
    actividades = ActividadSimulacion.objects.select_related('usuario', 'laboratorio').all()
    data_actividades = [['ID', 'Usuario', 'Laboratorio', 'Fecha']]
    for a in actividades:
        data_actividades.append([a.id, a.usuario.nombre, a.laboratorio.nombre, a.fecha_actividad.strftime('%Y-%m-%d')])
    table_actividades = Table(data_actividades, hAlign='LEFT')
    table_actividades.setStyle(table_style)
    elements.append(Paragraph("Actividades de Simulación", styles['Heading2']))
    elements.append(table_actividades)
    elements.append(Paragraph("<br/>", styles['Normal']))

    # ==================== TABLA DE PAGOS ====================
    pagos = Pago.objects.select_related('usuario').all()
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
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe_completo.pdf"'
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