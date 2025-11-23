from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
import base64
from django.contrib.auth.hashers import make_password, check_password

from django.db.models.signals import post_migrate

# ======================
# MODELO: ROL
# ======================
class Rol(models.Model):
    TIPOS_ROL = [
        ('SuperAdmin', 'SuperAdmin'),
        ('Administrador', 'Administrador'),
        ('Profesor', 'Profesor'),
        ('Estudiante', 'Estudiante'),
    ]

    tipo = models.CharField(max_length=50, choices=TIPOS_ROL, unique=True)

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.tipo



# ======================
# MODELO: USUARIO
# ======================
class Usuario(models.Model):
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, related_name='usuarios')
    correo = models.CharField(max_length=100)
    contrasenia = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=[
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ] ,default='activo'
                              )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.correo} ({self.rol})"
    def set_password(self, raw_password):
        
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        
        return check_password(raw_password, self.password)


# ======================
# MODELO: PERSONA
# ======================
class Persona(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='personas')
    nombre = models.CharField(max_length=100)
    apellidoPaterno = models.CharField(max_length=100)
    apellidoMaterno = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=[
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ], default='activo')

    class Meta:
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'

    def __str__(self):
        return f"{self.nombre} {self.apellidoPaterno}"
# ======================
# MODELO: COLEGIO
# ======================
class Colegio(models.Model):
    nombre = models.CharField(max_length=200)
    direccion = models.CharField(max_length=300)
    estado = models.CharField(max_length=20, choices=[
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ],default='activo')

    class Meta:
        verbose_name = 'Colegio'
        verbose_name_plural = 'Colegios'

    def __str__(self):
        return self.nombre
    
# ======================
# MODELO: ADMINISTRADOR
# ======================
class Administrador(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='administradores')
    persona = models.ForeignKey('Persona', on_delete=models.SET_NULL, null=True, blank=True, related_name='administradores')
    colegio = models.ForeignKey('Colegio', on_delete=models.SET_NULL, null=True, blank=True, related_name='administradores')
    estado = models.CharField(max_length=20, choices=[
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ], default='Activo')
    
    class Meta:
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'

    def __str__(self):
        detalles = [self.usuario.correo]
        if self.persona:
            detalles.append(f"{self.persona.nombre} {self.persona.apellidoPaterno}")
        if self.colegio:
            detalles.append(f"({self.colegio.nombre})")
        return " - ".join(detalles)

# ======================
# MODELO: CONFIGURACIÓN VISUAL
# ======================
class ConfiguracionVisual(models.Model):
    colegio = models.OneToOneField(Colegio, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    color_primario = models.CharField(max_length=7, default='#007bff')
    color_secundario = models.CharField(max_length=7, default='#6c757d')
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración Visual'
        verbose_name_plural = 'Configuraciones Visuales'

    def __str__(self):
        return f"Configuración de {self.administrador.usuario.correo}"


# ======================
# MODELO: ESTUDIANTE
# ======================
class Estudiante(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='estudiantes')
    colegio = models.ForeignKey(Colegio, on_delete=models.CASCADE, related_name='estudiantes')
    curso = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=[
        ('Activo', 'activo'),
        ('Inactivo', 'inactivo'),
    ],default='Activo')

    class Meta:
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'

    def __str__(self):
        return f"Estudiante: {self.persona.nombre} {self.persona.apellidoPaterno}"


# ======================
# MODELO: PROFESOR
# ======================
class Profesor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='profesor')
    colegio = models.ForeignKey(Colegio, on_delete=models.CASCADE, related_name='profesores')
    curso = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=[
        ('Activo', 'activo'),
        ('Inactivo', 'inactivo'),
    ],default='Activo')

    class Meta:
        verbose_name = 'Profesor'
        verbose_name_plural = 'Profesores'

    def __str__(self):
        return f"Profesor: {self.usuario.first_name} {self.usuario.last_name}"


# ======================
# MODELO: CURSO
# ======================
class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE, related_name='cursos')
    estado = models.CharField(max_length=20, choices=[
        ('Activo', 'activo'),
        ('Inactivo', 'inactivo'),
    ],default='Activo')

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'

    def __str__(self):
        return self.nombre

# ======================
# MODELO: TEMA
# ======================
class Temas(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='temas')
    nombre_archivo = models.CharField(max_length=200)
    descripcion = models.TextField()
    numero = models.IntegerField(validators=[MinValueValidator(1)])
    estado = models.CharField(max_length=50, choices=[
        ('disponible', 'Disponible'),
        ('no disponible', 'No Disponible'),
    ], default='disponible')
    fecha_inicio = models.DateField()
    tamanio = models.IntegerField(help_text="Duración en horas o días")
    archivo = models.FileField(upload_to='tema/')
    class Meta:
        verbose_name = 'Temas'
        verbose_name_plural = 'Temas'
        ordering = ['curso', 'numero']

    def __str__(self):
        return f"{self.curso.nombre} - {self.nombre_archivo}"


# ======================
# MODELO: LABORATORIO
# ======================
class Laboratorio(models.Model):
    nombre = models.CharField(max_length=200)
    # ruta relativa dentro de MEDIA_ROOT donde se extrae el paquete (por ejemplo: 'laboratorios/23/')
    carpeta = models.CharField(max_length=300, blank=True, null=True)
    estado = models.CharField(max_length=50, choices=[
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('completado', 'Completado')
    ], default='activo')

    class Meta:
        verbose_name = 'Laboratorio'
        verbose_name_plural = 'Laboratorios'

    def __str__(self):
        return self.nombre


# ======================
# MODELO: COMPONENTES
# ======================
class Componente(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='componentes/', null=True, blank=True)
    modelo3D = models.FileField(upload_to='modelos3D/', null=True, blank=True)
    especificaciones = models.TextField(blank=True)
    video_explicacion = models.URLField(max_length=500, blank=True)
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.SET_NULL, null=True, blank=True, related_name='componentes')
    estado = models.CharField(max_length=20, choices=[
        ('Activo', 'activo'),
        ('Inactivo', 'inactivo'),
    ],default='Activo')
    
    class Meta:
        verbose_name = 'Componente'
        verbose_name_plural = 'Componentes'

    def __str__(self):
       
        if self.laboratorio:
            return f"{self.laboratorio.nombre} - {self.nombre}"
        return self.nombre


# ======================
# MODELO: MEMBRESÍA
# ======================
class Membresia(models.Model):
    TIPO_CHOICES = [
        ('basica', 'Básica'),
        ('premium', 'Premium'),
        ('empresarial', 'Empresarial')
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    periodo_total = models.IntegerField(help_text="Duración en días")
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    maximo_usuarios = models.IntegerField(validators=[MinValueValidator(1)])
    estado = models.CharField(max_length=50, choices=[
        ('activa', 'Activa'),
        ('vencida', 'Vencida'),
        ('cancelada', 'Cancelada'),
        ('suspendida', 'Suspendida')
    ], default='activa')

    class Meta:
        verbose_name = 'Membresía'
        verbose_name_plural = 'Membresías'

    def __str__(self):
        return self.nombre


# ======================
# MODELO: SUSCRIPCIÓN
# ======================
class Suscripcion(models.Model):
    colegio = models.ForeignKey(Colegio, on_delete=models.CASCADE, related_name='suscripciones')
    membresia = models.ForeignKey(Membresia, on_delete=models.CASCADE, related_name='suscripciones')
    usuarios_actuales = models.IntegerField(default=0)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    periodo_total = models.IntegerField(help_text="Duración en días")

    class Meta:
        verbose_name = 'Suscripción'
        verbose_name_plural = 'Suscripciones'

    def __str__(self):
        return f"{self.colegio.nombre} - {self.membresia.nombre}"


# ======================
# MODELO: PAGO
# ======================
class Pago(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    metodo = models.CharField(max_length=50, choices=[
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('efectivo', 'Efectivo'),
        ('otro', 'Otro')
    ])
    estado = models.CharField(max_length=50, choices=[
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado')
    ], default='pendiente')
    comprobante = models.FileField(upload_to='comprobantes/', null=True, blank=True)

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-fecha']

    def __str__(self):
     return f"Pago {self.id} - {self.usuario.correo} - ${self.monto}"


 # ======================
# MODULO: CONTENIDO TEORICO
# ======================   
class Documento(models.Model):
    ESTADO_CHOICES = [
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
        ('En revisión', 'En revisión'),
    ]
    tema = models.ForeignKey(
        'Temas',
        on_delete=models.CASCADE,
        related_name='documentos',
        null = False,
        verbose_name="Temas"
    )
    nombre = models.CharField(max_length=255, verbose_name="Nombre del documento")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    archivo_pdf = models.FileField(upload_to="pdfs/")  
    nombre_archivo = models.CharField(max_length=255, verbose_name="Nombre del archivo", blank=True)
    tamaño = models.IntegerField(verbose_name="Tamaño (bytes)", null=True, blank=True)
    
    
    categoria = models.CharField(
    max_length=50, 
    default='fisica_general',
    verbose_name="Categoría"
    )
    estado = models.CharField(max_length=20, choices=[
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ],default='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización", null=True)
    
    class Meta:
        db_table = 'documentos'
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.nombre
    
    def get_pdf_base64(self):
        """Devuelve el PDF en base64 para incrustar en HTML"""
        if self.archivo_pdf:
            return base64.b64encode(self.archivo_pdf).decode('utf-8')
        return ""
    
    def get_tamaño_formateado(self):
        """Devuelve el tamaño formateado (KB, MB)"""
        if self.tamaño:
            if self.tamaño < 1024:
                return f"{self.tamaño} B"
            elif self.tamaño < 1024 * 1024:
                return f"{self.tamaño / 1024:.1f} KB"
            else:
                return f"{self.tamaño / (1024 * 1024):.1f} MB"
        return "0 B"
    


def crear_roles(sender, **kwargs):
    for tipo, _ in Rol.TIPOS_ROL:
        Rol.objects.get_or_create(tipo=tipo)

post_migrate.connect(crear_roles, sender=None)
  
    
