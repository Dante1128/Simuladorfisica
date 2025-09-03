from django import forms
from .models import Usuario
import re

from django import forms
from .models import Usuario

class RegistroUsuarioForm(forms.ModelForm):
    contrasena = forms.CharField(
        widget=forms.PasswordInput(),
        label="Contraseña"
    )
    confirmar_contrasena = forms.CharField(
        widget=forms.PasswordInput(),
        label="Confirmar Contraseña"
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'correo', 'contrasena', 'tipo']

    # Validación de la contraseña
    def clean_contrasena(self):
        contrasena = self.cleaned_data.get('contrasena')

        if len(contrasena) < 6:
            raise forms.ValidationError("La contraseña debe tener al menos 6 caracteres.")
        if not re.search(r'[A-Z]', contrasena):
            raise forms.ValidationError("Debe contener al menos una letra mayúscula.")
        if not re.search(r'[a-z]', contrasena):
            raise forms.ValidationError("Debe contener al menos una letra minúscula.")
        if not re.search(r'\d', contrasena):
            raise forms.ValidationError("Debe contener al menos un número.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', contrasena):
            raise forms.ValidationError("Debe contener al menos un carácter especial.")

        return contrasena

    # Validar que coincidan contraseñas
    def clean(self):
        cleaned_data = super().clean()
        contrasena = cleaned_data.get("contrasena")
        confirmar = cleaned_data.get("confirmar_contrasena")

        if contrasena != confirmar:
            raise forms.ValidationError("Las contraseñas no coinciden.")



class CuentaClienteForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'correo', 'tipo']
        widgets = {
            'correo': forms.EmailInput(attrs={'readonly': 'readonly'}),  # Para que el correo no sea editable
        }
