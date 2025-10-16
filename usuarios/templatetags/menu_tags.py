from django import template
from usuarios.models import Componente, Usuario

register = template.Library()


@register.inclusion_tag('administrador/_componentes_menu.html', takes_context=True)
def componentes_menu(context):
    request = context.get('request')
    show = False

    # Primero intento obtener usuario por sesión (tu proyecto usa request.session['usuario_id'])
    try:
        usuario_id = None
        if request:
            usuario_id = request.session.get('usuario_id')

        if usuario_id:
            usuario_obj = Usuario.objects.filter(id=usuario_id).select_related('rol').first()
            if usuario_obj and usuario_obj.rol and usuario_obj.rol.tipo.lower() == 'administrador':
                show = True
        else:
            # fallback: si hay un request.user con rol attribute
            user = context.get('user')
            if user and hasattr(user, 'rol') and getattr(user, 'rol'):
                try:
                    if user.rol.tipo.lower() == 'administrador':
                        show = True
                except Exception:
                    show = False
    except Exception:
        show = False

    count = Componente.objects.count()
    return {
        'show': show,
        'count': count,
        'request': request,
    }
