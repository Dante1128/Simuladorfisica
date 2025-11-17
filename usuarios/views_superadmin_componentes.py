from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from .models import Componente
from .forms import ComponenteForm

def superadmin_componentes_list(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    q = request.GET.get('q', '').strip()
    qs = Componente.objects.select_related('laboratorio').all()
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q) | Q(laboratorio__nombre__icontains=q))

    # paginación simple
    page = request.GET.get('page', 1)
    paginator = Paginator(qs, 12)  # 12 por página
    try:
        componentes_page = paginator.page(page)
    except PageNotAnInteger:
        componentes_page = paginator.page(1)
    except EmptyPage:
        componentes_page = paginator.page(paginator.num_pages)

    context = {
        'componentes': componentes_page,
        'page_obj': componentes_page,
        'paginator': paginator,
        'q': q,
    }
    return render(request, 'superadministrador/componentes_list.html', context)

def superadmin_componente_create(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    if request.method == 'POST':
        form = ComponenteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Componente creado correctamente')
            return redirect('superadmin_componentes_list')
    else:
        form = ComponenteForm()

    return render(request, 'superadministrador/componente_form.html', {'form': form, 'accion': 'Agregar'})

def superadmin_componente_update(request, pk):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    componente = get_object_or_404(Componente, pk=pk)
    if request.method == 'POST':
        form = ComponenteForm(request.POST, request.FILES, instance=componente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Componente actualizado correctamente')
            return redirect('superadmin_componentes_list')
    else:
        form = ComponenteForm(instance=componente)

    return render(request, 'superadministrador/componente_form.html', {'form': form, 'accion': 'Editar'})

def superadmin_componente_delete_confirm(request, pk):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    componente = get_object_or_404(Componente, pk=pk)
    if request.method == 'POST':
        try:
            componente.delete()
            messages.success(request, f'El componente "{componente.nombre}" ha sido eliminado')
            # Si es una petición AJAX, retornar JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('superadmin_componentes_list')
        except Exception as e:
            messages.error(request, f'Error al eliminar el componente: {str(e)}')
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            return redirect('superadmin_componentes_list')

    return render(request, 'superadministrador/componente_confirm_delete.html', {'componente': componente})


def superadmin_componente_form_partial(request, pk=None):
    """Retorna solo el formulario (sin base) para incrustarlo en un modal.
    No procesa POST aquí; el formulario debe publicar a las rutas existentes
    (superadmin_componente_create / superadmin_componente_update).
    """
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    # permitir pk via query param para llamadas AJAX: ?pk=123
    if not pk:
        try:
            pk = int(request.GET.get('pk')) if request.GET.get('pk') else None
        except ValueError:
            pk = None

    if pk:
        componente = get_object_or_404(Componente, pk=pk)
        form = ComponenteForm(instance=componente)
        action_url = reverse('superadmin_componente_update', kwargs={'pk': pk})
        titulo = 'Editar componente'
    else:
        componente = None
        form = ComponenteForm()
        action_url = reverse('superadmin_componente_create')
        titulo = 'Agregar componente'

    return render(request, 'superadministrador/componente_form_modal.html', {
        'form': form,
        'action_url': action_url,
        'titulo': titulo,
        'componente': componente,
    })