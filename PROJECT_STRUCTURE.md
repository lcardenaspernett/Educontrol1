# Estructura del Proyecto EduControl

## Estructura Principal
```
educontrol/
├── app/                         # Código principal de la aplicación
│   ├── __init__.py            # Inicialización de Flask
│   ├── models/                # Modelos de datos
│   │   └── __init__.py
│   ├── routes/                # Rutas principales
│   │   └── main_bp.py
│   ├── auth/                  # Autenticación
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── admin/                 # Administración
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── templates/         # Templates de admin
│   │       ├── dashboard.html
│   │       ├── nuevo.html
│   │       ├── estudiantes_nuevo.html
│   │       ├── docentes_nuevo.html
│   │       ├── directivos_nuevo.html
│   │       ├── padres_nuevo.html
│   │       └── asignaturas_nueva.html
│   ├── templates/            # Templates principales
│   │   ├── base.html
│   │   ├── login.html
│   │   └── register.html
│   └── static/               # Archivos estáticos
│       ├── css/
│       ├── js/
│       └── images/
├── config.py                 # Configuración de la aplicación
├── create_admin.py          # Script para crear admin
├── init_db.py               # Script para inicializar DB
├── instance/               # Configuración de instancia
├── migrations/             # Migraciones de DB
├── requirements.txt        # Dependencias
├── run.py                 # Punto de entrada
└── venv/                  # Entorno virtual
```
