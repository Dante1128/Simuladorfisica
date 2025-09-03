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
]
