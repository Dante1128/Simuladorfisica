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
    path('gestion-documentos/', views.gestion_documentos, name='gestion_documentos'),
    path('contenido-teorico/', views.contenido_teorico, name='contenido_teorico'),
    path('documentos/<int:documento_id>/descargar/', views.descargar_documento, name='descargar_documento'),
    path('documentos/<int:documento_id>/preview/', views.preview_documento, name='preview_documento')
   
]