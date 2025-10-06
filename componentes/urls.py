from django.urls import path
from . import views

app_name = 'componentes'

urlpatterns = [
    # cliente
    path('list/', views.ComponentListView.as_view(), name='list_client'),
    path('detalle/<int:pk>/', views.ComponentDetailView.as_view(), name='detail'),
    path('', views.ComponentListView.as_view(), name='list'),

    # laboratorio
    path('laboratorio/agregar/', views.agregar_laboratorio, name='agregar_laboratorio'),

    # admin interno
    path('admin/componentes/', views.AdminComponentListView.as_view(), name='admin_list'),
    path('admin/componentes/add/', views.AdminComponentCreateView.as_view(), name='admin_add'),
    path('admin/componentes/<int:pk>/edit/', views.AdminComponentUpdateView.as_view(), name='admin_edit'),
    path('admin/componentes/<int:pk>/delete/', views.AdminComponentDeleteView.as_view(), name='admin_delete'),

    # vista de gestion
    path('gestion/', views.gestion_componentes, name='gestion_componentes'),
]
