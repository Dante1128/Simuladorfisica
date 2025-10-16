from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('panel_superadmin/',views.panel_superadmin, name='panel_superadmin'),
    path('gestion_colegios/', views.gestion_colegios, name='gestion_colegios'),
    path('gestion_cursos/', views.gestion_cursos, name='gestion_cursos'),
    path('gestion_profesor/', views.gestion_profesor, name='gestion_profesor'),
    path('gestion_estudiante/', views.gestion_estudiante, name='gestion_estudiante'),
    path('panel_admin/', views.panel_admin, name='panel_admin'),
    path('panel_estudiante/', views.panel_estudiante, name='panel_estudiante'),
    path('panel_profesor/', views.panel_profesor, name='panel_profesor'),

    # =================================================================
    # NUEVAS URLs PARA INFORMES Y REPORTES
    # =================================================================
    
    # Dashboards principales
    path('informes/', views.informes_principal, name='informes_principal'),
    path('dashboard/superadmin/', views.dashboard_superadmin, name='dashboard_superadmin'),
    path('dashboard/administrador/', views.dashboard_administrador, name='dashboard_administrador'),
    path('dashboard/profesor/', views.dashboard_profesor, name='dashboard_profesor'),
    path('dashboard/estudiante/', views.dashboard_estudiante, name='dashboard_estudiante'),
    
    # APIs para datos en tiempo real
    path('api/estadisticas-tiempo-real/', views.api_estadisticas_tiempo_real, name='api_estadisticas_tiempo_real'),
    
    # Reportes PDF
    path('reportes/usuarios/', views.generar_reporte_pdf, {'tipo_reporte': 'usuarios'}, name='reporte_usuarios'),
    path('reportes/colegios/', views.generar_reporte_pdf, {'tipo_reporte': 'colegios'}, name='reporte_colegios'),
    path('reportes/suscripciones/', views.generar_reporte_pdf, {'tipo_reporte': 'suscripciones'}, name='reporte_suscripciones'),
    path('reportes/pagos/', views.generar_reporte_pdf, {'tipo_reporte': 'pagos'}, name='reporte_pagos'),
    path('reportes/estudiantes/', views.generar_reporte_pdf, {'tipo_reporte': 'estudiantes'}, name='reporte_estudiantes'),
    path('reportes/profesores/', views.generar_reporte_pdf, {'tipo_reporte': 'profesores'}, name='reporte_profesores'),
    path('reportes/cursos/', views.generar_reporte_pdf, {'tipo_reporte': 'cursos'}, name='reporte_cursos'),
    path('reportes/temas/', views.generar_reporte_pdf, {'tipo_reporte': 'temas'}, name='reporte_temas'),
    path('reportes/temas-disponibles/', views.generar_reporte_pdf, {'tipo_reporte': 'temas_disponibles'}, name='reporte_temas_disponibles'),
    path('reportes/laboratorios/', views.generar_reporte_pdf, {'tipo_reporte': 'laboratorios'}, name='reporte_laboratorios'),
    
    # URLs para AJAX y búsquedas
    path('buscar-colegios/', views.buscar_colegios, name='buscar_colegios'),
    path('editar-colegio/<int:colegio_id>/', views.editar_colegio, name='editar_colegio'),
    path('eliminar-colegio/<int:colegio_id>/', views.eliminar_colegio, name='eliminar_colegio'),
    path('exportar-colegios/', views.exportar_colegios, name='exportar_colegios'),
    path('gestion-documentos/', views.gestion_documentos, name='gestion_documentos'),
    path('contenido-teorico/', views.contenido_teorico, name='contenido_teorico'),
    path('documentos/<int:documento_id>/descargar/', views.descargar_documento, name='descargar_documento'),
    path('documentos/<int:documento_id>/preview/', views.preview_documento, name='preview_documento')
   
]