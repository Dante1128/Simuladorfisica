from django import forms
from .models import Usuario

class RegistroUsuarioForm(forms.ModelForm):
    contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder':'Ingresa su contresaña'}),
        label='Contraseña')
    
    confirmar_contrasena = forms.CharField(
        widget =forms.PasswordInput(attrs={'placeholder':'Confirme sus contraseña'}),
        label = "Confirma Contraseña")
    
    class Meta:
        model =  Usuario
        fields = ['nombre','apellido','correo','contrasena', 'tipo']
        widgets = {
            'nombre':forms.TextInput(attrs={'placeholder':'Ingrese su nombre'}),
            'apellido':forms.TextInput(attrs={'placeholder':'Ingrese su apellido'}),
            'correo':forms.EmailInput(attrs={'placeholder':'Ingrese su correo'}),
            'tipo':forms.Select(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = {
            'nombre': self.fields['nombre'],
            'apellido': self.fields['apellido'],
            'correo': self.fields['correo'],
            'contrasena': self.fields['contrasena'],
            'confirmar_contrasena': self.fields['confirmar_contrasena'],
            'tipo': self.fields['tipo'],
        }
    
    def clean(self):
        cleaned_data = super().clean()
        contrasena = cleaned_data.get("contrasena")
        confirmar_contrasena = cleaned_data.get("confirmar_contrasena")

        if contrasena and confirmar_contrasena and contrasena != confirmar_contrasena:
            self.add_error('confirmar_contrasena',"Las contraseñas no coinciden")