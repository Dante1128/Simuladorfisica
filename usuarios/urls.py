from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('panel_superadmin/',views.panel_superadmin, name='panel_superadmin'),
    
    # Rutas para Componentes (Superadministrador)
    path('superadmin/componentes/', views.superadmin_componentes_list, name='superadmin_componentes_list'),
    path('superadmin/componentes/agregar/', views.superadmin_componente_create, name='superadmin_componente_create'),
    path('superadmin/componentes/<int:pk>/editar/', views.superadmin_componente_update, name='superadmin_componente_update'),
    path('superadmin/componentes/<int:pk>/eliminar/', views.superadmin_componente_delete_confirm, name='superadmin_componente_delete_confirm'),
    # Partial/modal del formulario (opcional pk en la ruta)
    path('superadmin/componentes/form/', views.superadmin_componente_form_partial, name='superadmin_componente_form_partial'),
    # Rutas para Componentes
    path('componentes/', views.componentes_list, name='componentes_list'),
    path('componentes/agregar/', views.componente_create, name='componente_create'),
    path('componentes/<int:pk>/editar/', views.componente_update, name='componente_update'),
    path('componentes/<int:pk>/eliminar/', views.componente_delete_confirm, name='componente_delete_confirm'),
    # Rutas para Laboratorios (superadministrador)
    path('superadmin/laboratorios/', views.laboratorios_list, name='laboratorios_list'),
    path('superadmin/laboratorios/agregar/', views.laboratorio_create, name='laboratorio_create'),
    path('superadmin/laboratorios/<int:pk>/editar/', views.laboratorio_update, name='laboratorio_update'),
    path('superadmin/laboratorios/<int:pk>/eliminar/', views.laboratorio_delete_confirm, name='laboratorio_delete_confirm'),
    # Rutas para estudiantes
    path('estudiantes/laboratorios/', views.estudiantes_laboratorios_list, name='estudiantes_laboratorios_list'),
    path('estudiantes/laboratorios/<int:pk>/confirmar/', views.laboratorio_access_confirm, name='laboratorio_access_confirm'),
    path('estudiantes/laboratorios/<int:pk>/entrar/', views.laboratorio_entrar, name='laboratorio_entrar'),
    path('estudiantes/laboratorios/<int:pk>/serve/<path:filename>/', views.laboratorio_serve, name='laboratorio_serve'),
    path('gestion_colegios/', views.gestion_colegios, name='gestion_colegios'),
    path('gestion_administradores/', views.gestion_administradores, name='gestion_administradores'),
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
    # Rutas para Componentes
    path('componentes/', views.componentes_list, name='componentes_list'),
    path('componentes/agregar/', views.componente_create, name='componente_create'),
    path('componentes/<int:pk>/editar/', views.componente_update, name='componente_update'),
    path('componentes/<int:pk>/eliminar/', views.componente_delete_confirm, name='componente_delete_confirm'),
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
    path('gestion-documentos/', views.gestion_documentos, name='gestion_documentos'),
    path('contenido-teorico/', views.contenido_teorico, name='contenido_teorico'),
    path('documentos/<int:documento_id>/descargar/', views.descargar_documento, name='descargar_documento'),
    path('documentos/<int:documento_id>/preview/', views.preview_documento, name='preview_documento'),
    # Tarjetas de componentes para profesor y estudiante
    path('profesor/componentes/', views.componentes_profesor_tarjetas, name='componentes_profesor_tarjetas'),
    path('estudiante/componentes/', views.componentes_estudiante, name='componentes_estudiante'),  # Esta es la URL principal para componentes de estudiante
   
]