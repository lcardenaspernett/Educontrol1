from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import Usuario, Curso, Calificacion, Asistencia, db
from datetime import datetime, timedelta
from sqlalchemy import func, extract

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Función helper para calcular estadísticas del dashboard
def calcular_estadisticas_dashboard():
    """Calcula las estadísticas dinámicas para el dashboard"""
    try:
        # Fecha de hace un mes para comparaciones
        mes_pasado = datetime.now() - timedelta(days=30)
        
        # Totales actuales
        total_estudiantes = Usuario.query.filter_by(rol='alumno', activo=True).count()
        total_docentes = Usuario.query.filter_by(rol='profesor', activo=True).count()
        total_cursos = Curso.query.filter_by(activo=True).count()
        
        # Estudiantes del mes pasado para calcular crecimiento
        estudiantes_mes_pasado = Usuario.query.filter_by(rol='alumno', activo=True)\
            .filter(Usuario.fecha_creacion < mes_pasado).count()
        
        # Docentes del mes pasado
        docentes_mes_pasado = Usuario.query.filter_by(rol='profesor', activo=True)\
            .filter(Usuario.fecha_creacion < mes_pasado).count()
        
        # Cursos del mes pasado
        cursos_mes_pasado = Curso.query.filter_by(activo=True)\
            .filter(Curso.fecha_creacion < mes_pasado).count()
        
        # Calcular crecimientos
        crecimiento_estudiantes = 0
        if estudiantes_mes_pasado > 0:
            crecimiento_estudiantes = round(((total_estudiantes - estudiantes_mes_pasado) / estudiantes_mes_pasado) * 100, 1)
        elif total_estudiantes > 0:
            crecimiento_estudiantes = 100  # Primer mes con estudiantes
            
        crecimiento_docentes = 0
        if docentes_mes_pasado > 0:
            crecimiento_docentes = round(((total_docentes - docentes_mes_pasado) / docentes_mes_pasado) * 100, 1)
        elif total_docentes > 0:
            crecimiento_docentes = 100
            
        crecimiento_cursos = 0
        if cursos_mes_pasado > 0:
            crecimiento_cursos = round(((total_cursos - cursos_mes_pasado) / cursos_mes_pasado) * 100, 1)
        elif total_cursos > 0:
            crecimiento_cursos = 100
        
        # Promedio general de calificaciones
        promedio_actual = db.session.query(func.avg(Calificacion.nota)).scalar()
        promedio_actual = round(promedio_actual, 1) if promedio_actual else 0.0
        
        # Promedio del mes pasado
        promedio_mes_pasado = db.session.query(func.avg(Calificacion.nota))\
            .filter(Calificacion.fecha_evaluacion < mes_pasado).scalar()
        promedio_mes_pasado = promedio_mes_pasado if promedio_mes_pasado else 0.0
        
        # Variación del promedio
        variacion_promedio = round(promedio_actual - promedio_mes_pasado, 1) if promedio_mes_pasado > 0 else 0.0
        
        return {
            'total_estudiantes': total_estudiantes,
            'total_docentes': total_docentes,
            'total_cursos': total_cursos,
            'promedio_general': promedio_actual,
            'crecimiento_estudiantes': crecimiento_estudiantes,
            'crecimiento_docentes': crecimiento_docentes,
            'crecimiento_cursos': crecimiento_cursos,
            'variacion_promedio': variacion_promedio
        }
    except Exception as e:
        print(f"Error calculando estadísticas: {e}")
        return {
            'total_estudiantes': 0,
            'total_docentes': 0,
            'total_cursos': 0,
            'promedio_general': 0.0,
            'crecimiento_estudiantes': 0,
            'crecimiento_docentes': 0,
            'crecimiento_cursos': 0,
            'variacion_promedio': 0.0
        }

# Generar actividades recientes dinámicas
def generar_actividades_recientes():
    """Genera actividades recientes basadas en datos reales"""
    actividades = []
    
    try:
        # Últimos usuarios registrados
        ultimos_usuarios = Usuario.query.filter_by(activo=True)\
            .order_by(Usuario.fecha_creacion.desc()).limit(3).all()
        
        for usuario in ultimos_usuarios:
            dias_desde_registro = (datetime.now() - usuario.fecha_creacion).days
            if dias_desde_registro == 0:
                tiempo = "Hoy"
            elif dias_desde_registro == 1:
                tiempo = "Ayer"
            else:
                tiempo = f"Hace {dias_desde_registro} días"
                
            actividades.append({
                'usuario': f"{usuario.nombre} {usuario.apellido}",
                'descripcion': f"Nuevo {usuario.rol} registrado en el sistema",
                'tiempo_relativo': tiempo
            })
        
        # Últimas calificaciones
        ultimas_calificaciones = Calificacion.query\
            .join(Usuario, Calificacion.alumno_id == Usuario.id)\
            .order_by(Calificacion.fecha_evaluacion.desc()).limit(2).all()
        
        for calificacion in ultimas_calificaciones:
            dias_desde_calificacion = (datetime.now().date() - calificacion.fecha_evaluacion.date()).days
            if dias_desde_calificacion == 0:
                tiempo = "Hoy"
            elif dias_desde_calificacion == 1:
                tiempo = "Ayer"
            else:
                tiempo = f"Hace {dias_desde_calificacion} días"
                
            actividades.append({
                'usuario': f"{calificacion.alumno.nombre}",
                'descripcion': f"Nueva calificación: {calificacion.nota}/{calificacion.nota_maxima}",
                'tiempo_relativo': tiempo
            })
        
    except Exception as e:
        print(f"Error generando actividades: {e}")
    
    return actividades[:5]  # Máximo 5 actividades

# NUEVAS RUTAS PARA DATOS DE GRÁFICOS

@admin_bp.route('/api/dashboard-stats')
@login_required
def dashboard_stats():
    """Endpoint para obtener estadísticas del dashboard en JSON"""
    if current_user.rol != 'admin':
        return jsonify({'error': 'Acceso no autorizado'}), 403
    
    stats = calcular_estadisticas_dashboard()
    return jsonify(stats)

@admin_bp.route('/api/chart-data/<period>')
@login_required
def chart_data(period):
    """Endpoint para datos de gráficos según el período solicitado"""
    if current_user.rol != 'admin':
        return jsonify({'error': 'Acceso no autorizado'}), 403
    
    try:
        # Determinar rango de fechas según el período
        end_date = datetime.now()
        if period == '7d':
            start_date = end_date - timedelta(days=7)
            date_format = '%Y-%m-%d'
            interval = 'day'
        elif period == '30d':
            start_date = end_date - timedelta(days=30)
            date_format = '%Y-%m-%d'
            interval = 'day'
        elif period == '90d':
            start_date = end_date - timedelta(days=90)
            date_format = '%Y-%m'
            interval = 'month'
        else:
            start_date = end_date - timedelta(days=7)
            date_format = '%Y-%m-%d'
            interval = 'day'
        
        # Datos de registros de usuarios por día/mes
        if interval == 'day':
            usuario_data = db.session.query(
                func.date(Usuario.fecha_creacion).label('fecha'),
                func.count(Usuario.id).label('total')
            ).filter(
                Usuario.fecha_creacion >= start_date,
                Usuario.fecha_creacion <= end_date,
                Usuario.activo == True
            ).group_by(func.date(Usuario.fecha_creacion)).all()
        else:
            usuario_data = db.session.query(
                func.date_format(Usuario.fecha_creacion, '%Y-%m').label('fecha'),
                func.count(Usuario.id).label('total')
            ).filter(
                Usuario.fecha_creacion >= start_date,
                Usuario.fecha_creacion <= end_date,
                Usuario.activo == True
            ).group_by(func.date_format(Usuario.fecha_creacion, '%Y-%m')).all()
        
        # Formatear datos para Chart.js
        labels = []
        estudiantes_data = []
        docentes_data = []
        
        # Crear fechas completas para el período
        current_date = start_date
        while current_date <= end_date:
            if interval == 'day':
                label = current_date.strftime('%d/%m')
                date_key = current_date.strftime('%Y-%m-%d')
            else:
                label = current_date.strftime('%m/%Y')
                date_key = current_date.strftime('%Y-%m')
            
            labels.append(label)
            
            # Contar estudiantes y docentes para esta fecha
            estudiantes_count = Usuario.query.filter(
                Usuario.fecha_creacion <= current_date,
                Usuario.rol == 'alumno',
                Usuario.activo == True
            ).count()
            
            docentes_count = Usuario.query.filter(
                Usuario.fecha_creacion <= current_date,
                Usuario.rol == 'profesor',
                Usuario.activo == True
            ).count()
            
            estudiantes_data.append(estudiantes_count)
            docentes_data.append(docentes_count)
            
            # Incrementar fecha
            if interval == 'day':
                current_date += timedelta(days=1)
            else:
                # Aproximación para mes (30 días)
                current_date += timedelta(days=30)
        
        return jsonify({
            'labels': labels,
            'datasets': [
                {
                    'label': 'Estudiantes',
                    'data': estudiantes_data,
                    'borderColor': '#8E2DE2',
                    'backgroundColor': 'rgba(142, 45, 226, 0.1)',
                    'fill': True,
                    'tension': 0.4
                },
                {
                    'label': 'Docentes',
                    'data': docentes_data,
                    'borderColor': '#10B981',
                    'backgroundColor': 'rgba(16, 185, 129, 0.1)',
                    'fill': True,
                    'tension': 0.4
                }
            ]
        })
        
    except Exception as e:
        print(f"Error obteniendo datos del gráfico: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@admin_bp.route('/api/calificaciones-chart')
@login_required
def calificaciones_chart():
    """Endpoint para gráfico de distribución de calificaciones"""
    if current_user.rol != 'admin':
        return jsonify({'error': 'Acceso no autorizado'}), 403
    
    try:
        # Distribución de calificaciones por rangos
        rangos = [
            ('Excelente (90-100)', 90, 100),
            ('Bueno (80-89)', 80, 89),
            ('Aceptable (70-79)', 70, 79),
            ('Deficiente (60-69)', 60, 69),
            ('Insuficiente (0-59)', 0, 59)
        ]
        
        labels = []
        data = []
        colors = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#6B7280']
        
        for i, (label, min_nota, max_nota) in enumerate(rangos):
            count = Calificacion.query.filter(
                Calificacion.nota >= min_nota,
                Calificacion.nota <= max_nota
            ).count()
            
            labels.append(label.split(' ')[0])  # Solo la palabra (Excelente, Bueno, etc.)
            data.append(count)
        
        return jsonify({
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': colors,
                'borderWidth': 0
            }]
        })
        
    except Exception as e:
        print(f"Error obteniendo datos de calificaciones: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# RUTA PRINCIPAL DEL DASHBOARD (MODIFICADA)
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal con datos dinámicos"""
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.index'))
    
    # Obtener estadísticas
    stats = calcular_estadisticas_dashboard()
    
    # Obtener actividades recientes
    actividades_recientes = generar_actividades_recientes()
    
    # Generar tareas dinámicas basadas en el estado del sistema
    proximas_tareas = []
    
    if stats['total_estudiantes'] == 0:
        proximas_tareas.append({
            'descripcion': 'Registrar primeros estudiantes',
            'fecha_relativa': 'Prioridad alta',
            'tipo': 'primary',
            'icono': '👥'
        })
    
    if stats['total_docentes'] == 0:
        proximas_tareas.append({
            'descripcion': 'Agregar docentes al sistema',
            'fecha_relativa': 'Siguiente paso',
            'tipo': 'success',
            'icono': '👨‍🏫'
        })
    
    if stats['total_cursos'] == 0:
        proximas_tareas.append({
            'descripcion': 'Crear estructura de cursos',
            'fecha_relativa': 'Planificar',
            'tipo': 'warning',
            'icono': '📚'
        })
    
    # Si todo está configurado, agregar tareas de mantenimiento
    if stats['total_estudiantes'] > 0 and stats['total_docentes'] > 0:
        proximas_tareas.append({
            'descripcion': 'Revisar calificaciones pendientes',
            'fecha_relativa': 'Esta semana',
            'tipo': 'info',
            'icono': '📝'
        })
        proximas_tareas.append({
            'descripcion': 'Generar reportes mensuales',
            'fecha_relativa': 'Fin de mes',
            'tipo': 'secondary',
            'icono': '📊'
        })
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         actividades_recientes=actividades_recientes,
                         proximas_tareas=proximas_tareas)

# RESTO DE RUTAS EXISTENTES (SIN CAMBIOS)

@admin_bp.route('/estudiantes')
@login_required
def estudiantes():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    estudiantes = Usuario.query.filter_by(rol='alumno').all()
    return render_template('admin/estudiantes.html', estudiantes=estudiantes)

@admin_bp.route('/docentes')
@login_required
def docentes():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    docentes = Usuario.query.filter_by(rol='profesor').all()
    return render_template('admin/docentes.html', docentes=docentes)

@admin_bp.route('/directivos')
@login_required
def directivos():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    directivos = Usuario.query.filter_by(rol='directivo').all()
    return render_template('admin/directivos.html', directivos=directivos)

@admin_bp.route('/padres')
@login_required
def padres():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    padres = Usuario.query.filter_by(rol='padre').all()
    return render_template('admin/padres.html', padres=padres)

@admin_bp.route('/agregar_usuario')
@login_required
def agregar_usuario():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/agregar_usuario.html')

@admin_bp.route('/asignaturas')
@login_required
def asignaturas():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/asignaturas.html')

@admin_bp.route('/evaluaciones')
@login_required
def evaluaciones():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/evaluaciones.html')

@admin_bp.route('/reportes_rendimiento')
@login_required
def reportes_rendimiento():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/reportes_rendimiento.html')

@admin_bp.route('/nivelaciones')
@login_required
def nivelaciones():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/nivelaciones.html')

@admin_bp.route('/boletines')
@login_required
def boletines():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/boletines.html')

@admin_bp.route('/asistencias')
@login_required
def asistencias():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/asistencias.html')

@admin_bp.route('/observador')
@login_required
def observador():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/observador.html')

@admin_bp.route('/reportes_convivencia')
@login_required
def reportes_convivencia():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/reportes_convivencia.html')

@admin_bp.route('/tutorias')
@login_required
def tutorias():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/tutorias.html')

@admin_bp.route('/agenda')
@login_required
def agenda():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/agenda.html')

@admin_bp.route('/comunicados')
@login_required
def comunicados():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/comunicados.html')

@admin_bp.route('/notificaciones')
@login_required
def notificaciones():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/notificaciones.html')

@admin_bp.route('/contenidos')
@login_required
def contenidos():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/contenidos.html')

@admin_bp.route('/materiales')
@login_required
def materiales():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/materiales.html')

@admin_bp.route('/actividades')
@login_required
def actividades():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/actividades.html')

@admin_bp.route('/foros')
@login_required
def foros():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/foros.html')

@admin_bp.route('/periodos')
@login_required
def periodos():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/periodos.html')

@admin_bp.route('/roles_permisos')
@login_required
def roles_permisos():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/roles_permisos.html')

@admin_bp.route('/calendario_academico')
@login_required
def calendario_academico():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/calendario_academico.html')

@admin_bp.route('/importar_exportar')
@login_required
def importar_exportar():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/importar_exportar.html')

@admin_bp.route('/backup')
@login_required
def backup():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/backup.html')

@admin_bp.route('/nuevo')
@login_required
def nuevo():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/nuevo.html')

@admin_bp.route('/estudiantes/nuevo')
@login_required
def estudiantes_nuevo():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/estudiantes_nuevo.html')

@admin_bp.route('/docentes/nuevo')
@login_required
def docentes_nuevo():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/docentes_nuevo.html')

@admin_bp.route('/directivos/nuevo')
@login_required
def directivos_nuevo():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/directivos_nuevo.html')

@admin_bp.route('/padres/nuevo')
@login_required
def padres_nuevo():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/padres_nuevo.html')

@admin_bp.route('/asignaturas/nueva')
@login_required
def asignaturas_nueva():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/asignaturas_nueva.html')