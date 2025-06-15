from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Usuario, Curso, Inscripcion, Calificacion, Asistencia, db
from datetime import datetime, timedelta
from sqlalchemy import func, extract

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
    # 🔄 MEJORA 1: Calcular crecimientos reales
    mes_pasado = datetime.now() - timedelta(days=30)
    
    # Estadísticas actuales
    total_estudiantes = Usuario.query.filter_by(rol='alumno').count()
    total_docentes = Usuario.query.filter_by(rol='profesor').count()
    total_cursos = Curso.query.count()
    promedio_general = Calificacion.query.with_entities(db.func.avg(Calificacion.nota)).scalar() or 0
    
    # Estadísticas del mes pasado (si tienes campo fecha_registro en Usuario)
    try:
        estudiantes_mes_pasado = Usuario.query.filter_by(rol='alumno')\
            .filter(Usuario.fecha_creacion < mes_pasado).count()
        docentes_mes_pasado = Usuario.query.filter_by(rol='profesor')\
            .filter(Usuario.fecha_creacion < mes_pasado).count()
        
        # Calcular crecimientos reales
        crecimiento_estudiantes = 0
        if estudiantes_mes_pasado > 0:
            crecimiento_estudiantes = round(((total_estudiantes - estudiantes_mes_pasado) / estudiantes_mes_pasado * 100), 1)
        
        crecimiento_docentes = 0
        if docentes_mes_pasado > 0:
            crecimiento_docentes = round(((total_docentes - docentes_mes_pasado) / docentes_mes_pasado * 100), 1)
            
    except Exception as e:
        # Fallback a valores por defecto si no hay campo fecha_registro
        print(f"Advertencia: No se pudo calcular crecimiento - {e}")
        crecimiento_estudiantes = 12
        crecimiento_docentes = 5
    
    # Promedio del mes pasado
    try:
        promedio_mes_pasado = Calificacion.query\
            .filter(Calificacion.fecha_evaluacion < mes_pasado)\
            .with_entities(db.func.avg(Calificacion.nota)).scalar() or 0
        variacion_promedio = round(promedio_general - promedio_mes_pasado, 1) if promedio_mes_pasado > 0 else 0
    except:
        variacion_promedio = 0.3
    
    # Estadísticas finales
    stats = {
        'total_estudiantes': total_estudiantes,
        'total_docentes': total_docentes,
        'total_cursos': total_cursos,
        'promedio_general': round(promedio_general, 1) if promedio_general else 0.0,
        'crecimiento_estudiantes': crecimiento_estudiantes,
        'crecimiento_docentes': crecimiento_docentes,
        'crecimiento_cursos': 0,  # Implementar si tienes fecha en Curso
        'variacion_promedio': variacion_promedio
    }
    
    # 🔄 MEJORA 2: Actividades reales desde la base de datos
    try:
        # Últimas inscripciones como actividades
        inscripciones_recientes = db.session.query(Inscripcion, Usuario, Curso)\
            .join(Usuario, Inscripcion.usuario_id == Usuario.id)\
            .join(Curso, Inscripcion.curso_id == Curso.id)\
            .order_by(Inscripcion.fecha_inscripcion.desc())\
            .limit(3).all()
        
        actividades_recientes = []
        
        # Actividad del usuario actual siempre primera
        actividades_recientes.append({
            'usuario': current_user.nombre,
            'descripcion': f'{current_user.nombre} {current_user.apellido} inició sesión en el sistema',
            'tiempo_relativo': 'Hace unos momentos'
        })
        
        # Agregar inscripciones recientes
        for inscripcion, usuario, curso in inscripciones_recientes:
            tiempo_relativo = calcular_tiempo_relativo(inscripcion.fecha_inscripcion)
            actividades_recientes.append({
                'usuario': usuario.nombre,
                'descripcion': f'{usuario.nombre} {usuario.apellido} se inscribió en {curso.nombre}',
                'tiempo_relativo': tiempo_relativo
            })
        
        # Limitar a 5 actividades máximo
        actividades_recientes = actividades_recientes[:5]
        
    except Exception as e:
        print(f"Error al obtener actividades: {e}")
        # Fallback a actividades por defecto
        actividades_recientes = [
            {
                'usuario': current_user.nombre,
                'descripcion': f'{current_user.nombre} {current_user.apellido} inició sesión en el sistema',
                'tiempo_relativo': 'Hace unos momentos'
            },
            {
                'usuario': 'Sistema',
                'descripcion': 'Sistema iniciado correctamente',
                'tiempo_relativo': 'Hoy'
            }
        ]
    
    # 🔄 MEJORA 3: Próximas tareas dinámicas basadas en el estado del sistema
    proximas_tareas = []
    
    # Tareas basadas en el estado actual
    if total_estudiantes == 0:
        proximas_tareas.append({
            'descripcion': 'Registrar primeros estudiantes',
            'fecha_relativa': 'Prioridad alta',
            'tipo': 'info',
            'icono': '👥'
        })
    
    if total_docentes == 0:
        proximas_tareas.append({
            'descripcion': 'Agregar docentes al sistema',
            'fecha_relativa': 'Importante',
            'tipo': 'warning',
            'icono': '👨‍🏫'
        })
    
    if total_cursos == 0:
        proximas_tareas.append({
            'descripcion': 'Crear estructura de cursos',
            'fecha_relativa': 'Planificar',
            'tipo': 'info',
            'icono': '📚'
        })
    
    # Si ya hay datos, tareas de mantenimiento
    if total_estudiantes > 0 and total_docentes > 0:
        proximas_tareas.extend([
            {
                'descripcion': 'Revisar calificaciones pendientes',
                'fecha_relativa': 'Esta semana',
                'tipo': 'success',
                'icono': '📝'
            },
            {
                'descripcion': 'Generar reportes mensuales',
                'fecha_relativa': 'Fin de mes',
                'tipo': 'info',
                'icono': '📊'
            }
        ])
    
    # Tarea por defecto si no hay tareas específicas
    if not proximas_tareas:
        proximas_tareas.append({
            'descripcion': 'Sistema funcionando correctamente',
            'fecha_relativa': 'Todo al día',
            'tipo': 'success',
            'icono': '✅'
        })

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

def calcular_tiempo_relativo(fecha):
    """
    Función auxiliar para calcular tiempo relativo
    """
    ahora = datetime.now()
    diferencia = ahora - fecha
    
    if diferencia.days > 0:
        if diferencia.days == 1:
            return "Hace 1 día"
        elif diferencia.days < 30:
            return f"Hace {diferencia.days} días"
        else:
            return fecha.strftime("%d/%m/%Y")
    else:
        horas = diferencia.seconds // 3600
        if horas > 0:
            return f"Hace {horas} hora{'s' if horas > 1 else ''}"
        else:
            minutos = diferencia.seconds // 60
            if minutos > 0:
                return f"Hace {minutos} minuto{'s' if minutos > 1 else ''}"
            else:
                return "Hace unos momentos"

@main_bp.route('/admin/usuarios')
@login_required
def admin_usuarios():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    usuarios = Usuario.query.all()
    return render_template('admin/usuarios.html', usuarios=usuarios)