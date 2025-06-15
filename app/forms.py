from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, FloatField, DateField, BooleanField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional, Regexp
from wtforms.widgets import TextArea
from datetime import datetime, date

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[
        DataRequired(message='El usuario es obligatorio'),
        Length(min=4, max=25, message='El usuario debe tener entre 4 y 25 caracteres')
    ], render_kw={"placeholder": "Ingresa tu usuario"})
    
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria')
    ], render_kw={"placeholder": "Ingresa tu contraseña"})
    
    remember_me = BooleanField('Recordarme')

class UsuarioBaseForm(FlaskForm):
    """Formulario base para todos los tipos de usuarios"""
    username = StringField('Usuario', validators=[
        DataRequired(message='El usuario es obligatorio'),
        Length(min=4, max=25, message='El usuario debe tener entre 4 y 25 caracteres'),
        Regexp('^[A-Za-z0-9_]+$', message='El usuario solo puede contener letras, números y guiones bajos')
    ], render_kw={"placeholder": "ej: juan_perez"})
    
    email = StringField('Correo Electrónico', validators=[
        DataRequired(message='El email es obligatorio'),
        Email(message='Formato de email inválido'),
        Length(max=120, message='El email es demasiado largo')
    ], render_kw={"placeholder": "ejemplo@correo.com"})
    
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria'),
        Length(min=6, max=100, message='La contraseña debe tener al menos 6 caracteres')
    ], render_kw={"placeholder": "Mínimo 6 caracteres"})
    
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(message='Confirma la contraseña'),
        EqualTo('password', message='Las contraseñas no coinciden')
    ], render_kw={"placeholder": "Repite la contraseña"})
    
    nombre = StringField('Nombre(s)', validators=[
        DataRequired(message='El nombre es obligatorio'),
        Length(min=2, max=100, message='El nombre debe tener entre 2 y 100 caracteres'),
        Regexp('^[A-Za-zÀ-ÿ\u00f1\u00d1\s]+$', message='El nombre solo puede contener letras y espacios')
    ], render_kw={"placeholder": "Nombres completos"})
    
    apellido = StringField('Apellido(s)', validators=[
        DataRequired(message='El apellido es obligatorio'),
        Length(min=2, max=100, message='El apellido debe tener entre 2 y 100 caracteres'),
        Regexp('^[A-Za-zÀ-ÿ\u00f1\u00d1\s]+$', message='El apellido solo puede contener letras y espacios')
    ], render_kw={"placeholder": "Apellidos completos"})

class EstudianteForm(UsuarioBaseForm):
    """Formulario específico para estudiantes"""
    rol = HiddenField(default='alumno')
    
    # Información personal adicional
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[
        DataRequired(message='La fecha de nacimiento es obligatoria')
    ], render_kw={"max": date.today().strftime('%Y-%m-%d')})
    
    documento_identidad = StringField('Documento de Identidad', validators=[
        DataRequired(message='El documento es obligatorio'),
        Length(min=6, max=20, message='El documento debe tener entre 6 y 20 caracteres'),
        Regexp('^[0-9]+$', message='El documento solo puede contener números')
    ], render_kw={"placeholder": "Número de documento"})
    
    tipo_documento = SelectField('Tipo de Documento', choices=[
        ('cedula', 'Cédula de Ciudadanía'),
        ('tarjeta_identidad', 'Tarjeta de Identidad'),
        ('cedula_extranjeria', 'Cédula de Extranjería'),
        ('pasaporte', 'Pasaporte')
    ], validators=[DataRequired(message='Selecciona el tipo de documento')])
    
    genero = SelectField('Género', choices=[
        ('', 'Seleccionar...'),
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
        ('otro', 'Otro'),
        ('prefiero_no_decir', 'Prefiero no decir')
    ], validators=[DataRequired(message='Selecciona el género')])
    
    # Información de contacto
    telefono = StringField('Teléfono', validators=[
        Optional(),
        Length(min=7, max=15, message='El teléfono debe tener entre 7 y 15 dígitos'),
        Regexp('^[0-9\s\-\+\(\)]+$', message='Formato de teléfono inválido')
    ], render_kw={"placeholder": "Ej: 300 123 4567"})
    
    direccion = TextAreaField('Dirección de Residencia', validators=[
        Optional(),
        Length(max=200, message='La dirección es demasiado larga')
    ], render_kw={"placeholder": "Dirección completa", "rows": 3})
    
    # Información académica
    grado = SelectField('Grado/Curso', choices=[
        ('', 'Seleccionar grado...'),
        ('6', 'Sexto (6°)'),
        ('7', 'Séptimo (7°)'),
        ('8', 'Octavo (8°)'),
        ('9', 'Noveno (9°)'),
        ('10', 'Décimo (10°)'),
        ('11', 'Once (11°)')
    ], validators=[DataRequired(message='Selecciona el grado')])
    
    # Información del acudiente
    nombre_acudiente = StringField('Nombre del Acudiente', validators=[
        DataRequired(message='El nombre del acudiente es obligatorio'),
        Length(min=2, max=100, message='El nombre debe tener entre 2 y 100 caracteres')
    ], render_kw={"placeholder": "Nombre completo del acudiente"})
    
    telefono_acudiente = StringField('Teléfono del Acudiente', validators=[
        DataRequired(message='El teléfono del acudiente es obligatorio'),
        Length(min=7, max=15, message='El teléfono debe tener entre 7 y 15 dígitos'),
        Regexp('^[0-9\s\-\+\(\)]+$', message='Formato de teléfono inválido')
    ], render_kw={"placeholder": "Teléfono de contacto"})
    
    # Información médica básica
    eps = StringField('EPS/Seguro Médico', validators=[
        Optional(),
        Length(max=100, message='Nombre de EPS demasiado largo')
    ], render_kw={"placeholder": "Nombre de la EPS"})
    
    observaciones_medicas = TextAreaField('Observaciones Médicas', validators=[
        Optional(),
        Length(max=500, message='Las observaciones son demasiado largas')
    ], render_kw={"placeholder": "Alergias, medicamentos, condiciones especiales...", "rows": 3})

class DocenteForm(UsuarioBaseForm):
    """Formulario específico para docentes"""
    rol = HiddenField(default='profesor')
    
    # Información personal
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[
        DataRequired(message='La fecha de nacimiento es obligatoria')
    ], render_kw={"max": date.today().strftime('%Y-%m-%d')})
    
    documento_identidad = StringField('Cédula de Ciudadanía', validators=[
        DataRequired(message='La cédula es obligatoria'),
        Length(min=6, max=20, message='La cédula debe tener entre 6 y 20 caracteres'),
        Regexp('^[0-9]+$', message='La cédula solo puede contener números')
    ], render_kw={"placeholder": "Número de cédula"})
    
    genero = SelectField('Género', choices=[
        ('', 'Seleccionar...'),
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
        ('otro', 'Otro'),
        ('prefiero_no_decir', 'Prefiero no decir')
    ], validators=[DataRequired(message='Selecciona el género')])
    
    # Información de contacto
    telefono = StringField('Teléfono', validators=[
        DataRequired(message='El teléfono es obligatorio'),
        Length(min=7, max=15, message='El teléfono debe tener entre 7 y 15 dígitos'),
        Regexp('^[0-9\s\-\+\(\)]+$', message='Formato de teléfono inválido')
    ], render_kw={"placeholder": "Teléfono principal"})
    
    telefono_emergencia = StringField('Teléfono de Emergencia', validators=[
        Optional(),
        Length(min=7, max=15, message='El teléfono debe tener entre 7 y 15 dígitos'),
        Regexp('^[0-9\s\-\+\(\)]+$', message='Formato de teléfono inválido')
    ], render_kw={"placeholder": "Contacto de emergencia"})
    
    direccion = TextAreaField('Dirección de Residencia', validators=[
        DataRequired(message='La dirección es obligatoria'),
        Length(max=200, message='La dirección es demasiado larga')
    ], render_kw={"placeholder": "Dirección completa", "rows": 3})
    
    # Información académica y profesional
    titulo_profesional = StringField('Título Profesional', validators=[
        DataRequired(message='El título profesional es obligatorio'),
        Length(min=5, max=150, message='El título debe tener entre 5 y 150 caracteres')
    ], render_kw={"placeholder": "Ej: Licenciado en Matemáticas"})
    
    universidad = StringField('Universidad/Institución', validators=[
        DataRequired(message='La universidad es obligatoria'),
        Length(min=3, max=150, message='El nombre debe tener entre 3 y 150 caracteres')
    ], render_kw={"placeholder": "Nombre de la institución"})
    
    año_graduacion = IntegerField('Año de Graduación', validators=[
        DataRequired(message='El año de graduación es obligatorio'),
        NumberRange(min=1970, max=datetime.now().year, 
                   message=f'Año inválido (1970-{datetime.now().year})')
    ], render_kw={"placeholder": "Ej: 2020"})
    
    especializaciones = TextAreaField('Especializaciones/Posgrados', validators=[
        Optional(),
        Length(max=300, message='El texto es demasiado largo')
    ], render_kw={"placeholder": "Menciona especializaciones, maestrías, etc.", "rows": 3})
    
    # Experiencia laboral
    años_experiencia = IntegerField('Años de Experiencia', validators=[
        DataRequired(message='Los años de experiencia son obligatorios'),
        NumberRange(min=0, max=50, message='Años de experiencia inválidos (0-50)')
    ], render_kw={"placeholder": "Ej: 5"})
    
    # Asignaturas que puede enseñar
    asignaturas_especialidad = TextAreaField('Asignaturas de Especialidad', validators=[
        DataRequired(message='Especifica las asignaturas que puedes enseñar'),
        Length(min=5, max=300, message='Debe tener entre 5 y 300 caracteres')
    ], render_kw={"placeholder": "Ej: Matemáticas, Álgebra, Geometría, Cálculo", "rows": 3})
    
    # Disponibilidad
    jornada = SelectField('Jornada Laboral', choices=[
        ('', 'Seleccionar jornada...'),
        ('mañana', 'Jornada Mañana'),
        ('tarde', 'Jornada Tarde'),
        ('completa', 'Jornada Completa'),
        ('nocturna', 'Jornada Nocturna')
    ], validators=[DataRequired(message='Selecciona la jornada')])

class DirectivoForm(UsuarioBaseForm):
    """Formulario específico para directivos"""
    rol = HiddenField(default='directivo')
    
    # Información personal
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[
        DataRequired(message='La fecha de nacimiento es obligatoria')
    ], render_kw={"max": date.today().strftime('%Y-%m-%d')})
    
    documento_identidad = StringField('Cédula de Ciudadanía', validators=[
        DataRequired(message='La cédula es obligatoria'),
        Length(min=6, max=20, message='La cédula debe tener entre 6 y 20 caracteres'),
        Regexp('^[0-9]+$', message='La cédula solo puede contener números')
    ], render_kw={"placeholder": "Número de cédula"})
    
    genero = SelectField('Género', choices=[
        ('', 'Seleccionar...'),
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
        ('otro', 'Otro'),
        ('prefiero_no_decir', 'Prefiero no decir')
    ], validators=[DataRequired(message='Selecciona el género')])
    
    # Información de contacto
    telefono = StringField('Teléfono', validators=[
        DataRequired(message='El teléfono es obligatorio'),
        Length(min=7, max=15, message='El teléfono debe tener entre 7 y 15 dígitos'),
        Regexp('^[0-9\s\-\+\(\)]+$', message='Formato de teléfono inválido')
    ], render_kw={"placeholder": "Teléfono principal"})
    
    direccion = TextAreaField('Dirección de Residencia', validators=[
        DataRequired(message='La dirección es obligatoria'),
        Length(max=200, message='La dirección es demasiado larga')
    ], render_kw={"placeholder": "Dirección completa", "rows": 3})
    
    # Información académica y profesional
    titulo_profesional = StringField('Título Profesional', validators=[
        DataRequired(message='El título profesional es obligatorio'),
        Length(min=5, max=150, message='El título debe tener entre 5 y 150 caracteres')
    ], render_kw={"placeholder": "Ej: Especialista en Administración Educativa"})
    
    universidad = StringField('Universidad/Institución', validators=[
        DataRequired(message='La universidad es obligatoria'),
        Length(min=3, max=150, message='El nombre debe tener entre 3 y 150 caracteres')
    ], render_kw={"placeholder": "Nombre de la institución"})
    
    # Cargo y responsabilidades
    cargo_directivo = SelectField('Cargo Directivo', choices=[
        ('', 'Seleccionar cargo...'),
        ('rector', 'Rector(a)'),
        ('vicerrector', 'Vicerrector(a)'),
        ('coordinador_academico', 'Coordinador(a) Académico'),
        ('coordinador_convivencia', 'Coordinador(a) de Convivencia'),
        ('coordinador_administrativo', 'Coordinador(a) Administrativo'),
        ('secretario_academico', 'Secretario(a) Académico'),
        ('orientador', 'Orientador(a)'),
        ('otro', 'Otro Cargo Directivo')
    ], validators=[DataRequired(message='Selecciona el cargo')])
    
    años_experiencia_directiva = IntegerField('Años de Experiencia Directiva', validators=[
        DataRequired(message='Los años de experiencia son obligatorios'),
        NumberRange(min=0, max=50, message='Años de experiencia inválidos (0-50)')
    ], render_kw={"placeholder": "Ej: 8"})
    
    areas_responsabilidad = TextAreaField('Áreas de Responsabilidad', validators=[
        DataRequired(message='Especifica las áreas de responsabilidad'),
        Length(min=10, max=500, message='Debe tener entre 10 y 500 caracteres')
    ], render_kw={"placeholder": "Describe las principales responsabilidades del cargo", "rows": 4})

class PadreForm(UsuarioBaseForm):
    """Formulario específico para padres/acudientes"""
    rol = HiddenField(default='padre')
    
    # Información personal
    documento_identidad = StringField('Cédula de Ciudadanía', validators=[
        DataRequired(message='La cédula es obligatoria'),
        Length(min=6, max=20, message='La cédula debe tener entre 6 y 20 caracteres'),
        Regexp('^[0-9]+$', message='La cédula solo puede contener números')
    ], render_kw={"placeholder": "Número de cédula"})
    
    genero = SelectField('Género', choices=[
        ('', 'Seleccionar...'),
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
        ('otro', 'Otro'),
        ('prefiero_no_decir', 'Prefiero no decir')
    ], validators=[DataRequired(message='Selecciona el género')])
    
    # Información de contacto
    telefono = StringField('Teléfono Principal', validators=[
        DataRequired(message='El teléfono es obligatorio'),
        Length(min=7, max=15, message='El teléfono debe tener entre 7 y 15 dígitos'),
        Regexp('^[0-9\s\-\+\(\)]+$', message='Formato de teléfono inválido')
    ], render_kw={"placeholder": "Teléfono principal"})
    
    telefono_trabajo = StringField('Teléfono de Trabajo', validators=[
        Optional(),
        Length(min=7, max=15, message='El teléfono debe tener entre 7 y 15 dígitos'),
        Regexp('^[0-9\s\-\+\(\)]+$', message='Formato de teléfono inválido')
    ], render_kw={"placeholder": "Teléfono del trabajo"})
    
    direccion = TextAreaField('Dirección de Residencia', validators=[
        DataRequired(message='La dirección es obligatoria'),
        Length(max=200, message='La dirección es demasiado larga')
    ], render_kw={"placeholder": "Dirección completa", "rows": 3})
    
    # Información laboral
    ocupacion = StringField('Ocupación/Profesión', validators=[
        DataRequired(message='La ocupación es obligatoria'),
        Length(min=3, max=100, message='La ocupación debe tener entre 3 y 100 caracteres')
    ], render_kw={"placeholder": "Ej: Ingeniero, Docente, Comerciante"})
    
    empresa = StringField('Empresa/Lugar de Trabajo', validators=[
        Optional(),
        Length(max=150, message='El nombre de la empresa es demasiado largo')
    ], render_kw={"placeholder": "Nombre de la empresa (opcional)"})
    
    # Relación con el estudiante
    parentesco = SelectField('Parentesco con el Estudiante', choices=[
        ('', 'Seleccionar parentesco...'),
        ('padre', 'Padre'),
        ('madre', 'Madre'),
        ('abuelo', 'Abuelo'),
        ('abuela', 'Abuela'),
        ('tio', 'Tío'),
        ('tia', 'Tía'),
        ('hermano', 'Hermano'),
        ('hermana', 'Hermana'),
        ('tutor_legal', 'Tutor Legal'),
        ('otro', 'Otro Familiar')
    ], validators=[DataRequired(message='Selecciona el parentesco')])
    
    autorizado_recoger = BooleanField('Autorizado para Recoger al Estudiante', default=True)
    
    # Información adicional
    estado_civil = SelectField('Estado Civil', choices=[
        ('', 'Seleccionar...'),
        ('soltero', 'Soltero(a)'),
        ('casado', 'Casado(a)'),
        ('union_libre', 'Unión Libre'),
        ('divorciado', 'Divorciado(a)'),
        ('viudo', 'Viudo(a)'),
        ('separado', 'Separado(a)')
    ], validators=[Optional()])
    
    nivel_educativo = SelectField('Nivel Educativo', choices=[
        ('', 'Seleccionar...'),
        ('primaria', 'Educación Primaria'),
        ('secundaria', 'Educación Secundaria'),
        ('tecnico', 'Técnico'),
        ('tecnologo', 'Tecnólogo'),
        ('profesional', 'Profesional Universitario'),
        ('especializacion', 'Especialización'),
        ('maestria', 'Maestría'),
        ('doctorado', 'Doctorado')
    ], validators=[Optional()])

# Formularios adicionales para otras funcionalidades

class CursoForm(FlaskForm):
    """Formulario para crear/editar cursos"""
    nombre = StringField('Nombre del Curso', validators=[
        DataRequired(message='El nombre del curso es obligatorio'),
        Length(min=3, max=100, message='El nombre debe tener entre 3 y 100 caracteres')
    ], render_kw={"placeholder": "Ej: Matemáticas 10°"})
    
    codigo = StringField('Código del Curso', validators=[
        DataRequired(message='El código es obligatorio'),
        Length(min=3, max=20, message='El código debe tener entre 3 y 20 caracteres'),
        Regexp('^[A-Za-z0-9_-]+$', message='Solo letras, números, guiones y guiones bajos')
    ], render_kw={"placeholder": "Ej: MAT10A"})
    
    descripcion = TextAreaField('Descripción', validators=[
        Optional(),
        Length(max=500, message='La descripción es demasiado larga')
    ], render_kw={"placeholder": "Descripción del curso (opcional)", "rows": 4})
    
    profesor_id = SelectField('Profesor Asignado', coerce=int, validators=[
        Optional()
    ])
    
    def __init__(self, *args, **kwargs):
        super(CursoForm, self).__init__(*args, **kwargs)
        # Las opciones de profesor se cargarán dinámicamente en la vista

class CalificacionForm(FlaskForm):
    """Formulario para registrar calificaciones"""
    alumno_id = SelectField('Estudiante', coerce=int, validators=[
        DataRequired(message='Selecciona un estudiante')
    ])
    
    curso_id = SelectField('Curso', coerce=int, validators=[
        DataRequired(message='Selecciona un curso')
    ])
    
    tipo_evaluacion = SelectField('Tipo de Evaluación', choices=[
        ('', 'Seleccionar tipo...'),
        ('quiz', 'Quiz'),
        ('parcial', 'Examen Parcial'),
        ('final', 'Examen Final'),
        ('tarea', 'Tarea'),
        ('proyecto', 'Proyecto'),
        ('participacion', 'Participación'),
        ('laboratorio', 'Laboratorio'),
        ('otro', 'Otro')
    ], validators=[DataRequired(message='Selecciona el tipo de evaluación')])
    
    nota = FloatField('Calificación', validators=[
        DataRequired(message='La calificación es obligatoria'),
        NumberRange(min=0, max=100, message='La nota debe estar entre 0 y 100')
    ], render_kw={"placeholder": "Ej: 85.5", "step": "0.1"})
    
    nota_maxima = FloatField('Nota Máxima', validators=[
        DataRequired(message='La nota máxima es obligatoria'),
        NumberRange(min=1, max=100, message='La nota máxima debe estar entre 1 y 100')
    ], default=100.0, render_kw={"step": "0.1"})
    
    fecha_evaluacion = DateField('Fecha de Evaluación', validators=[
        DataRequired(message='La fecha es obligatoria')
    ], default=date.today)
    
    observaciones = TextAreaField('Observaciones', validators=[
        Optional(),
        Length(max=500, message='Las observaciones son demasiado largas')
    ], render_kw={"placeholder": "Comentarios sobre la evaluación (opcional)", "rows": 3})
    
    def __init__(self, *args, **kwargs):
        super(CalificacionForm, self).__init__(*args, **kwargs)
        # Las opciones se cargarán dinámicamente en la vista