from app import create_app, db
from app.models import Usuario

app = create_app()

with app.app_context():
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
        db.session.commit()
        print("Usuario administrador creado:")
        print("Usuario: admin")
        print("Contraseña: admin123")
    else:
        print("El usuario administrador ya existe")
