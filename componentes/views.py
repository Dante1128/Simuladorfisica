from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django import forms
from .models import Component
from usuarios.models import Laboratorio

class ComponentListView(ListView):
    model = Component
    template_name = 'componentes/list_client.html'
    context_object_name = 'componentes'

class ComponentDetailView(DetailView):
    model = Component
    template_name = 'componentes/detail_client.html'
    context_object_name = 'componente'

# Vistas de administración (puedes personalizarlas luego)
class AdminComponentListView(ListView):
    model = Component
    template_name = 'componentes/admin_list.html'
    context_object_name = 'componentes'

class AdminComponentCreateView(CreateView):
    model = Component
    fields = '__all__'
    template_name = 'componentes/admin_form.html'
    success_url = reverse_lazy('componentes:gestion_componentes')

class AdminComponentUpdateView(UpdateView):
    model = Component
    fields = '__all__'
    template_name = 'componentes/admin_form.html'
    success_url = reverse_lazy('componentes:gestion_componentes')

class AdminComponentDeleteView(DeleteView):
    model = Component
    template_name = 'componentes/admin_component_confirm_delete.html'
    success_url = reverse_lazy('componentes:gestion_componentes')

def gestion_componentes(request):
    componentes = Component.objects.all()
    laboratorios = Laboratorio.objects.all()
    return render(request, 'componentes/gestion_componentes.html', {
        'componentes': componentes,
        'laboratorios': laboratorios
    })

# Formulario para agregar laboratorio
class LaboratorioForm(forms.ModelForm):
    class Meta:
        model = Laboratorio
        fields = ['nombre_simulacion', 'descripcion', 'estado', 'archivo_laboratorio']

def agregar_laboratorio(request):
    if request.method == 'POST':
        form = LaboratorioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('panel_admin')
    else:
        form = LaboratorioForm()
    return render(request, 'laboratorios/agregar_laboratorio.html', {'form': form})
    return render(request, 'componentes/gestion_componentes.html', {
        'componentes': componentes,
        'laboratorios': laboratorios
    })
