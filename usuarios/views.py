from django.shortcuts import render, redirect
from .forms import RegistroUsuarioForm
from django.contrib.auth.hashers import make_password

def index(request):
    return render(request, 'usuarios/index.html')



def registro_usuario(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit= False)
            usuario.contrasena = make_password(form.cleaned_data["contrasena"])
            usuario.save()
            return redirect('registro')
    else:
         form =  RegistroUsuarioForm()

    return render(request, 'usuarios/registro.html',{"form":form})
