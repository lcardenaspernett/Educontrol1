# -*- coding: utf-8 -*-
import os
import sys

# Agregar el directorio actual al path
sys.path.insert(0, os.path.abspath('.'))

# Configurar FLASK_APP
os.environ['FLASK_APP'] = 'run.py'

from app import create_app, db
from app.models import Usuario

def setup_database():
    """Configurar la base de datos desde cero."""
    
    # Crear la aplicacion
    app = create_app()
    
    with app.app_context():
        # Crear todas las tablas
        print("Creando tablas de base de datos...")
        db.create_all()
        
        # Crear usuario administrador
        print("Creando usuario administrador...")
        admin = Usuario.query.filter_by(username='admin').first()
        if not admin:
            admin = Usuario(
                username='admin',
                email='admin@educontrol.com',
                rol='admin',
                nombre='Administrador',
                apellido='Sistema'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("Administrador creado")
        else:
            print("Administrador ya existe")
        
        # Crear usuarios de prueba
        print("Creando usuarios de prueba...")
        
        # Profesor
        profesor = Usuario.query.filter_by(username='profesor1').first()
        if not profesor:
            profesor = Usuario(
                username='profesor1',
                email='profesor1@educontrol.com',
                rol='profesor',
                nombre='Juan',
                apellido='Perez'
            )
            profesor.set_password('profesor123')
            db.session.add(profesor)
            print("Profesor creado")
        else:
            print("Profesor ya existe")
        
        # Alumno
        alumno = Usuario.query.filter_by(username='alumno1').first()
        if not alumno:
            alumno = Usuario(
                username='alumno1',
                email='alumno1@educontrol.com',
                rol='alumno',
                nombre='Maria',
                apellido='Garcia'
            )
            alumno.set_password('alumno123')
            db.session.add(alumno)
            print("Alumno creado")
        else:
            print("Alumno ya existe")
        
        # Guardar cambios
        db.session.commit()
        
        print("\nBase de datos configurada exitosamente!")
        print("\nCredenciales de acceso:")
        print("Administrador: admin / admin123")
        print("Profesor: profesor1 / profesor123")
        print("Alumno: alumno1 / alumno123")

if __name__ == '__main__':
    setup_database()
