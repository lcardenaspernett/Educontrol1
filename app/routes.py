from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Usuario, Curso, Inscripcion, Calificacion, Asistencia, db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/home')
def home():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Calcular estadísticas dinámicas
    stats = {
        'total_estudiantes': Usuario.query.filter_by(rol='alumno').count(),
        'total_docentes': Usuario.query.filter_by(rol='profesor').count(),
        'total_cursos': Curso.query.count(),
        'promedio_general': Calificacion.query.with_entities(db.func.avg(Calificacion.nota)).scalar() or 0,
        'crecimiento_estudiantes': 12,  # Puedes calcular esto usando fechas
        'crecimiento_docentes': 5,
        'crecimiento_cursos': 0,
        'variacion_promedio': 0.3
    }
    
    # Actividades recientes
    actividades_recientes = [
        {
            'usuario': current_user.nombre,
            'descripcion': f'{current_user.nombre} {current_user.apellido} inició sesión en el sistema',
            'tiempo_relativo': 'Hace unos momentos'
        }
    ]
    
    # Próximas tareas
    proximas_tareas = [
        {
            'descripcion': 'Configurar sistema educativo',
            'fecha_relativa': 'Prioridad alta',
            'tipo': 'info',
            'icono': '🚀'
        }
    ]

    if current_user.rol == 'admin':
        return render_template('admin/dashboard.html', 
                             usuario=current_user,
                             stats=stats,
                             actividades_recientes=actividades_recientes,
                             proximas_tareas=proximas_tareas)
    elif current_user.rol == 'profesor':
        return render_template('profesor/dashboard.html', usuario=current_user)
    elif current_user.rol == 'alumno':
        return render_template('alumno/dashboard.html', usuario=current_user)
    else:
        flash('Rol no reconocido', 'error')
        return redirect(url_for('auth.logout'))

@main_bp.route('/admin/usuarios')
@login_required
def admin_usuarios():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    usuarios = Usuario.query.all()
    return render_template('admin/usuarios.html', usuarios=usuarios)
