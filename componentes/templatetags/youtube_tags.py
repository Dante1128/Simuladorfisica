# componentes/templatetags/youtube_tags.py
from django import template
import re
register = template.Library()

@register.filter
def youtube_id(url):
    """
    Extrae el id de un URL de youtube (funciona con varias formas).
    """
    if not url:
        return ''
    # patrones comunes
    patterns = [
        r'v=([^&]+)',
        r'youtu\.be\/([^?&]+)',
        r'embed\/([^?&]+)'
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return ''
