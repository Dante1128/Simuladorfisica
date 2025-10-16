from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('panel_admin/',views.panel_admin, name='panel_admin'),
    # Rutas para Componentes
    path('componentes/', views.componentes_list, name='componentes_list'),
    path('componentes/agregar/', views.componente_create, name='componente_create'),
    path('componentes/<int:pk>/editar/', views.componente_update, name='componente_update'),
    path('componentes/<int:pk>/eliminar/', views.componente_delete_confirm, name='componente_delete_confirm'),
   
]