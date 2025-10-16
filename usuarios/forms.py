from django import forms
from .models import Componente


class ComponenteForm(forms.ModelForm):
	class Meta:
		model = Componente
		fields = ['nombre', 'descripcion', 'imagen', 'modelo3D', 'especificaciones', 'video_explicacion', 'tema', 'laboratorio']
		widgets = {
			'descripcion': forms.Textarea(attrs={'rows': 3}),
			'especificaciones': forms.Textarea(attrs={'rows': 3}),
		}
