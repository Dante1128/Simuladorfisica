from django import forms
from .models import Componente, Laboratorio


class ComponenteForm(forms.ModelForm):
	class Meta:
		model = Componente
		fields = ['nombre', 'descripcion', 'imagen', 'modelo3D', 'especificaciones', 'video_explicacion', 'tema', 'laboratorio']
		widgets = {
			'descripcion': forms.Textarea(attrs={'rows': 3}),
			'especificaciones': forms.Textarea(attrs={'rows': 3}),
		}


class LaboratorioForm(forms.ModelForm):
	# Campo auxiliar para subir un zip que contenga la carpeta completa
	archivo_zip = forms.FileField(required=False, help_text='Sube un archivo .zip que contenga imágenes, modelos 3D y el HTML para A-Frame')

	class Meta:
		model = Laboratorio
		fields = ['nombre', 'estado', 'archivo_zip']
		widgets = {
			# archivo eliminado del modelo; usar solo archivo_zip para subir paquetes
		}
    
	def clean_archivo_zip(self):
		f = self.cleaned_data.get('archivo_zip')
		if not f:
			return f

		from django.conf import settings
		# Usar el límite configurado en settings.py (500MB por defecto)
		max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 524288000)  # 500MB por defecto
		if f.size > max_size:
			max_size_mb = max_size / (1024 * 1024)
			raise forms.ValidationError(f'El archivo zip es demasiado grande (máx {int(max_size_mb)} MB).')

		# extensión .zip
		name = f.name.lower()
		if not name.endswith('.zip'):
			raise forms.ValidationError('El archivo debe ser un .zip')

		# opcional: tipo MIME aproximado
		content_type = f.content_type
		if content_type and 'zip' not in content_type and 'octet-stream' not in content_type:
			# no bloquear estrictamente, solo advertir posible incompatibilidad
			raise forms.ValidationError('El archivo subido no parece ser un archivo zip válido.')

		return f
