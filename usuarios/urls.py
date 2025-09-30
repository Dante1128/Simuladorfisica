from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("registro/", views.registro_usuario, name="registro"),
    path('login/', views.login, name='login'),
    path('home-cliente/', views.home_cliente, name='home_cliente'),
    path('base-cliente/', views.base_cliente, name='base_cliente'),
    path('cuenta-cliente/', views.cuenta_cliente, name='cuenta_cliente'),
    path('logout/', views.logout, name='logout'),
    path('gestion-documentos/', views.gestion_documentos, name='gestion_documentos'),
    path('contenido-teorico/', views.contenido_teorico, name='contenido_teorico'),
    path('documentos/<int:documento_id>/descargar/', views.descargar_documento, name='descargar_documento'),
    path('documentos/<int:documento_id>/preview/', views.preview_documento, name='preview_documento'),
    path('gestion-usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('panel_admin/', views.panel_admin, name='panel_admin'),
    path('base-admin/', views.base_admin, name='base_admin'),
    path('perfil-admin/', views.perfil_admin, name='perfil_admin'),

    # REPORTES
    path('dashboard-reportes/', views.dashboard_reportes, name='dashboard_reportes'),
    path('generar-informe-completo-pdf/', views.generar_informe_completo_pdf, name='generar_informe_completo_pdf'),
]