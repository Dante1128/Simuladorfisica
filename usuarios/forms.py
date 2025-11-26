from django import forms
from .models import Componente, Laboratorio, Membresia


class ComponenteForm(forms.ModelForm):
	class Meta:
		model = Componente
		fields = ['nombre', 'descripcion', 'imagen', 'modelo3D', 'especificaciones', 'video_explicacion', 'laboratorio']
		widgets = {
			'descripcion': forms.Textarea(attrs={'rows': 3}),
			'especificaciones': forms.Textarea(attrs={'rows': 3}),
		}



class LaboratorioForm(forms.ModelForm):
    # Campo para indicar la URL del laboratorio (A-Frame, HTML + recursos)
    url = forms.URLField(
        required=True,
        help_text='Ingresa la URL completa donde se encuentra el laboratorio (por ejemplo, GitHub Pages)'
    )

    class Meta:
        model = Laboratorio
        fields = ['nombre', 'estado', 'url']
