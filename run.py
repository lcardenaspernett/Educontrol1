import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from app import create_app
from app.models import db, Usuario, Curso, Inscripcion, Calificacion, Asistencia

# Crear la aplicación
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Usuario=Usuario, Curso=Curso, 
                Inscripcion=Inscripcion, Calificacion=Calificacion, 
                Asistencia=Asistencia)

@app.cli.command()
def init_db():
    """Inicializar la base de datos."""
    with app.app_context():
        db.drop_all()
        db.create_all()
        print('Base de datos inicializada.')

@app.cli.command()
def create_users():
    """Crear usuarios de prueba."""
    with app.app_context():
        # Admin
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
            print('Administrador creado: admin/admin123')
        
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
            print('Profesor creado: profesor1/profesor123')
        
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
            print('Alumno creado: alumno1/alumno123')
        
        db.session.commit()
        print('Usuarios creados exitosamente!')

if __name__ == '__main__':
    app.run(debug=True)
