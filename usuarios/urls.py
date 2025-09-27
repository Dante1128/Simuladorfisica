from django.urls import path
from django.contrib.auth import views as auth_views  # Importa las vistas de auth

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("registro/", views.registro_usuario, name="registro"),
    path('login/', views.login, name='login'),  # Usa tu vista personalizada de login
    path('home-cliente/', views.home_cliente, name='home_cliente'),
    path('base-cliente/', views.base_cliente, name='base_cliente'),
    path('cuenta-cliente/', views.cuenta_cliente, name='cuenta_cliente'),
    path('logout/', views.logout, name='logout'),
    # NUEVA URL PÚBLICA PARA GESTIÓN DE DOCUMENTOS
    path('gestion-documentos/', views.gestion_documentos, name='gestion_documentos'),
    path('contenido-teorico/', views.contenido_teorico, name='contenido_teorico'),
    path('documentos/<int:documento_id>/descargar/', views.descargar_documento, name='descargar_documento'),
    path('documentos/<int:documento_id>/preview/', views.preview_documento, name='preview_documento'),

# NUEVAS URLs PARA REPORTES (AGREGAR AL FINAL)
    
# DASHBOARD UNIFICADO (TODO EN UNO)
path('dashboard-reportes/', views.dashboard_reportes, name='dashboard_reportes'),

# PDF UNIFICADO
path('generar-informe-completo-pdf/', views.generar_informe_completo_pdf, name='generar_informe_completo_pdf'),

# COMENTADO PARA FUTURO USO
# path('reporte-usuarios/', views.reporte_usuarios, name='reporte_usuarios'),
# path('reporte-membresias/', views.reporte_membresias, name='reporte_membresias'),
# path('reporte-simulaciones/', views.reporte_simulaciones, name='reporte_simulaciones'),
# path('reporte-ingresos/', views.reporte_ingresos, name='reporte_ingresos'),
# path('api-estadisticas/', views.api_estadisticas, name='api_estadisticas'),
]
