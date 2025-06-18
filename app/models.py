from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import bcrypt

# Crear la instancia db aquí
db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum('admin', 'profesor', 'alumno', 'directivo', 'padre', name='rol_types'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Campos adicionales para estudiantes y usuarios
    documento = db.Column(db.String(20), unique=True, nullable=True)
    tipo_documento = db.Column(db.String(5), default='CC')
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    genero = db.Column(db.String(1), nullable=True)  # M/F
    telefono = db.Column(db.String(15), nullable=True)
    direccion = db.Column(db.Text, nullable=True)
    ciudad = db.Column(db.String(50), nullable=True)
    barrio = db.Column(db.String(100), nullable=True)
    
    # Campos específicos para estudiantes
    grado = db.Column(db.Integer, nullable=True)
    seccion = db.Column(db.String(1), nullable=True)
    
    # Relaciones
    cursos_profesor = db.relationship('Curso', backref='profesor', lazy=True, foreign_keys='Curso.profesor_id')
    inscripciones = db.relationship('Inscripcion', backref='alumno', lazy=True)
    calificaciones = db.relationship('Calificacion', backref='alumno', lazy=True)
    asistencias = db.relationship('Asistencia', backref='alumno', lazy=True)
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del usuario"""
        return f"{self.nombre} {self.apellido}"
    
    @property
    def edad(self):
        """Calcula la edad basada en la fecha de nacimiento"""
        if self.fecha_nacimiento:
            today = datetime.today().date()
            return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        return None
    
    def __repr__(self):
        return f'<Usuario {self.username}>'

class Curso(db.Model):
    __tablename__ = 'cursos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    profesor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    inscripciones = db.relationship('Inscripcion', backref='curso', lazy=True, cascade='all, delete-orphan')
    calificaciones = db.relationship('Calificacion', backref='curso', lazy=True, cascade='all, delete-orphan')
    asistencias = db.relationship('Asistencia', backref='curso', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Curso {self.nombre}>'

class Inscripcion(db.Model):
    __tablename__ = 'inscripciones'
    
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    fecha_inscripcion = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    __table_args__ = (db.UniqueConstraint('alumno_id', 'curso_id', name='unique_alumno_curso'),)

class Calificacion(db.Model):
    __tablename__ = 'calificaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    tipo_evaluacion = db.Column(db.String(50), nullable=False)
    nota = db.Column(db.Float, nullable=False)
    nota_maxima = db.Column(db.Float, default=100.0)
    observaciones = db.Column(db.Text)
    fecha_evaluacion = db.Column(db.DateTime, default=datetime.utcnow)

class Asistencia(db.Model):
    __tablename__ = 'asistencias'
    
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    presente = db.Column(db.Boolean, default=False)
    observaciones = db.Column(db.Text)
    
    __table_args__ = (db.UniqueConstraint('alumno_id', 'curso_id', 'fecha', name='unique_asistencia_dia'),)