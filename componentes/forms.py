from django import forms
from .models import Component
from usuarios.models import Laboratorio
import json

class ComponentForm(forms.ModelForm):
    class Meta:
        model = Component
        fields = '__all__'
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows':4}),
            'video_youtube': forms.URLInput(attrs={'placeholder':'https://www.youtube.com/watch?v=ID'}),
        }

class LaboratorioForm(forms.ModelForm):
    class Meta:
        model = Laboratorio
        fields = '__all__'
