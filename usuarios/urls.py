from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('panel_superadmin/',views.panel_superadmin, name='panel_superadmin'),
    # Rutas para Componentes
    path('componentes/', views.componentes_list, name='componentes_list'),
    path('componentes/agregar/', views.componente_create, name='componente_create'),
    path('componentes/<int:pk>/editar/', views.componente_update, name='componente_update'),
    path('componentes/<int:pk>/eliminar/', views.componente_delete_confirm, name='componente_delete_confirm'),
    path('gestion_colegios/', views.gestion_colegios, name='gestion_colegios'),
    path('gestion_cursos/', views.gestion_cursos, name='gestion_cursos'),
    path('gestion_profesor/', views.gestion_profesor, name='gestion_profesor'),
    path('gestion_estudiante/', views.gestion_estudiante, name='gestion_estudiante'),
    path('panel_admin/', views.panel_admin, name='panel_admin'),
    path('panel_estudiante/', views.panel_estudiante, name='panel_estudiante'),
    path('panel_profesor/', views.panel_profesor, name='panel_profesor'),
]