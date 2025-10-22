# PhysicsLab Pro


## 🛠️ Tecnologías

- Django 5.x
- PostgreSQL
- HTML5, CSS3, JavaScript

## ⚡ Instalación rápida

1. **Crea un entorno virtual (recomendado):**
   ```bash
   python -m venv env
   # En Windows:
   env\Scripts\activate
  

2. Clona el repositorio:
   ```bash
   git clone https://github.com/Dante1128/Simuladorfisica.git
   cd Simuladorfisica
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configura la base de datos en `settings.py`.

5. Aplica migraciones:
   ```bash
   python manage.py migrate
   ```

6. Ejecuta el servidor:
   ```bash
   python manage.py runserver
   ```
## Registro para poder acceder en rol administrador
```bash
   python manage.py shell
```

## Copiar lo siguente 
```
from usuarios.models import Rol, Usuario

# Crear rol SuperAdmin si no existe
rol_admin, created = Rol.objects.get_or_create(tipo="SuperAdmin")

# Crear usuario SuperAdmin solo si no existe
usuario, created_user = Usuario.objects.get_or_create(
    correo="d@gmail.com",
    defaults={
        'rol': rol_admin,
        'estado': "Activo",
    }
)

if created_user:
    usuario.set_password("1234")  # encripta correctamente la contraseña
    usuario.save()
    print("✅ Usuario SuperAdmin creado correctamente.")
else:
    print("⚠️ El usuario ya existe.")


   
```
## 📂 Estructura del proyecto

```
proyectosimuladorFisica/
├── usuarios/
├── templates/
│   └── usuarios/
├── static/
│   └── usuarios/
├── manage.py
├── requirements.txt
└── README.md
```



