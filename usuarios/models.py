# usuarios/models.py
from django.db import models
from django.utils import timezone  

class Usuario(models.Model):
    TIPO_USUARIO = [
        ('estudiante', 'Estudiante'),
        ('universitario', 'Universitario'),
        ('profesional', 'Profesional'),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=128)
    tipo = models.CharField(max_length=20, choices=TIPO_USUARIO, default='estudiante')

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.correo}) - {self.tipo}"

# ============ NUEVOS MODELOS PARA REPORTES ============

class Membresia(models.Model):
    TIPO_MEMBRESIA = [
        ('mensual', 'Mensual'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    ]
    
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('expirado', 'Expirado'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='membresias')
    tipo_membresia = models.CharField(max_length=20, choices=TIPO_MEMBRESIA)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_expiracion = models.DateTimeField()
    
    def __str__(self):
        return f"{self.usuario.correo} - {self.tipo_membresia}"

class Laboratorio(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    
    nombre_simulacion = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    archivo_laboratorio = models.FileField(upload_to='laboratorios/', blank=True)
    
    def __str__(self):
        return self.nombre_simulacion

class ActividadSimulacion(models.Model):
    """Modelo simplificado solo para simulaciones completadas"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='simulaciones_completadas')
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE)
    fecha_actividad = models.DateTimeField(default=timezone.now)
    duracion_minutos = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.usuario.correo} - {self.laboratorio.nombre_simulacion} - {self.fecha_actividad.date()}"

class Pago(models.Model):
    TIPO_MEMBRESIA = [
        ('mensual', 'Mensual'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pagos')
    membresia = models.ForeignKey(Membresia, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_membresia = models.CharField(max_length=20, choices=TIPO_MEMBRESIA)
    fecha_pago = models.DateTimeField(default=timezone.now)
    metodo_pago = models.CharField(max_length=50, default='tarjeta')
    
    def __str__(self):
        return f"{self.usuario.correo} - ${self.monto} - {self.fecha_pago.date()}"

# ============ MODELOS PARA REPORTES ESPECÍFICOS ============

class ReporteDashboard(models.Model):
    """Modelo principal para almacenar datos del dashboard con filtros por fecha"""
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    # Métricas principales
    total_usuarios = models.IntegerField()
    usuarios_activos = models.IntegerField()
    simulaciones_realizadas = models.IntegerField()
    ingresos_periodo = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Comparación con período anterior
    usuarios_activos_anterior = models.IntegerField(default=0)
    simulaciones_realizadas_anterior = models.IntegerField(default=0)
    
    # Fecha de generación del reporte
    fecha_generacion = models.DateTimeField(default=timezone.now)
    
    @property
    def porcentaje_usuarios(self):
        if self.usuarios_activos_anterior > 0:
            return round(((self.usuarios_activos - self.usuarios_activos_anterior) / self.usuarios_activos_anterior) * 100, 1)
        return 0
    
    @property
    def porcentaje_simulaciones(self):
        if self.simulaciones_realizadas_anterior > 0:
            return round(((self.simulaciones_realizadas - self.simulaciones_realizadas_anterior) / self.simulaciones_realizadas_anterior) * 100, 1)
        return 0
    
    def __str__(self):
        return f"Dashboard {self.fecha_inicio} - {self.fecha_fin}"

class ReporteUsuarios(models.Model):
    total_usuarios = models.IntegerField()
    usuarios_activos = models.IntegerField()
    usuarios_inactivos = models.IntegerField()
    fecha_reporte = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"Reporte Usuarios - {self.fecha_reporte}"

class ReporteMembresias(models.Model):
    total_membresias = models.IntegerField()
    membresias_mensuales = models.IntegerField()
    membresias_semestrales = models.IntegerField()
    membresias_anuales = models.IntegerField()
    fecha_reporte = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"Reporte Membresías - {self.fecha_reporte}"

class ReporteSimulaciones(models.Model):
    simulaciones_activas = models.IntegerField()
    simulaciones_totales = models.IntegerField()
    simulaciones_realizadas_mes = models.IntegerField(default=0)
    fecha_reporte = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"Reporte Simulaciones - {self.fecha_reporte}"

class ReporteIngresos(models.Model):
    ingresos_mensuales = models.DecimalField(max_digits=10, decimal_places=2)
    ingresos_anuales = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_reporte = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"Reporte Ingresos - {self.fecha_reporte}"
#=================================Fin de las tablas para reportes==============================