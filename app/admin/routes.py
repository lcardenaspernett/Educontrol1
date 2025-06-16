from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from app.models import Usuario, Curso, Calificacion, Asistencia, db
from app.forms import EstudianteForm, DocenteForm, DirectivoForm, PadreForm, CursoForm, CalificacionForm
from datetime import datetime, timedelta
from sqlalchemy import func, extract

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ============================================
# FUNCIONES HELPER PARA ESTADÍSTICAS
# ============================================

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

def verificar_admin():
    """Helper para verificar si el usuario actual es admin"""
    if current_user.rol != 'admin':
        flash('Acceso no autorizado. Se requieren permisos de administrador.', 'error')
        return False
    return True

# ============================================
# RUTAS DE API PARA GRÁFICOS (EXISTENTES)
# ============================================

@admin_bp.route('/api/dashboard-stats')
@login_required
def dashboard_stats():
    """Endpoint para obtener estadísticas del dashboard en JSON"""
    if not verificar_admin():
        return jsonify({'error': 'Acceso no autorizado'}), 403
    
    stats = calcular_estadisticas_dashboard()
    return jsonify(stats)

@admin_bp.route('/api/chart-data/<period>')
@login_required
def chart_data(period):
    """Endpoint para datos de gráficos según el período solicitado"""
    if not verificar_admin():
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
    if not verificar_admin():
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

# ============================================
# DASHBOARD PRINCIPAL
# ============================================

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal con datos dinámicos"""
    if not verificar_admin():
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

# ============================================
# GESTIÓN DE ESTUDIANTES
# ============================================

@admin_bp.route('/estudiantes')
@login_required
def estudiantes():
    """Lista de estudiantes"""
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    
    estudiantes = Usuario.query.filter_by(rol='alumno', activo=True).all()
    return render_template('admin/estudiantes.html', estudiantes=estudiantes)

@admin_bp.route('/estudiantes/nuevo', methods=['GET', 'POST'])
@login_required
def estudiantes_nuevo():
    """Formulario para crear nuevo estudiante"""
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    
    form = EstudianteForm()
    
    if form.validate_on_submit():
        try:
            # Verificar si el usuario o email ya existen
            usuario_existente = Usuario.query.filter(
                (Usuario.username == form.username.data) | 
                (Usuario.email == form.email.data)
            ).first()
            
            if usuario_existente:
                if usuario_existente.username == form.username.data:
                    flash('El nombre de usuario ya está en uso. Elige otro.', 'error')
                else:
                    flash('El email ya está registrado en el sistema.', 'error')
                return render_template('admin/estudiantes_nuevo.html', form=form)
            
            # Crear nuevo usuario estudiante
            estudiante = Usuario(
                username=form.username.data,
                email=form.email.data,
                rol='alumno',
                nombre=form.nombre.data,
                apellido=form.apellido.data,
                activo=True,
                fecha_creacion=datetime.utcnow()
            )
            
            # Establecer contraseña
            estudiante.set_password(form.password.data)
            
            # Agregar a la base de datos
            db.session.add(estudiante)
            db.session.commit()
            
            flash(f'Estudiante {form.nombre.data} {form.apellido.data} creado exitosamente.', 'success')
            return redirect(url_for('admin.estudiantes'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creando estudiante: {e}")
            flash('Error al crear el estudiante. Inténtalo de nuevo.', 'error')
    
    return render_template('admin/estudiantes_nuevo.html', form=form)

# ============================================
# GESTIÓN DE DOCENTES
# ============================================

@admin_bp.route('/docentes')
@login_required
def docentes():
    """Lista de docentes"""
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    
    docentes = Usuario.query.filter_by(rol='profesor', activo=True).all()
    return render_template('admin/docentes.html', docentes=docentes)

@admin_bp.route('/docentes/nuevo', methods=['GET', 'POST'])
@login_required
def docentes_nuevo():
    """Formulario para crear nuevo docente"""
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    
    form = DocenteForm()
    
    if form.validate_on_submit():
        try:
            # Verificar si el usuario o email ya existen
            usuario_existente = Usuario.query.filter(
                (Usuario.username == form.username.data) | 
                (Usuario.email == form.email.data)
            ).first()
            
            if usuario_existente:
                if usuario_existente.username == form.username.data:
                    flash('El nombre de usuario ya está en uso. Elige otro.', 'error')
                else:
                    flash('El email ya está registrado en el sistema.', 'error')
                return render_template('admin/docentes_nuevo.html', form=form)
            
            # Crear nuevo usuario docente
            docente = Usuario(
                username=form.username.data,
                email=form.email.data,
                rol='profesor',
                nombre=form.nombre.data,
                apellido=form.apellido.data,
                activo=True,
                fecha_creacion=datetime.utcnow()
            )
            
            # Establecer contraseña
            docente.set_password(form.password.data)
            
            # Agregar a la base de datos
            db.session.add(docente)
            db.session.commit()
            
            flash(f'Docente {form.nombre.data} {form.apellido.data} creado exitosamente.', 'success')
            return redirect(url_for('admin.docentes'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creando docente: {e}")
            flash('Error al crear el docente. Inténtalo de nuevo.', 'error')
    
    return render_template('admin/docentes_nuevo.html', form=form)

# ============================================
# GESTIÓN DE DIRECTIVOS
# ============================================

@admin_bp.route('/directivos')
@login_required
def directivos():
    """Lista de directivos"""
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    
    directivos = Usuario.query.filter_by(rol='directivo', activo=True).all()
    return render_template('admin/directivos.html', directivos=directivos)

@admin_bp.route('/directivos/nuevo', methods=['GET', 'POST'])
@login_required
def directivos_nuevo():
    """Formulario para crear nuevo directivo"""
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    
    form = DirectivoForm()
    
    if form.validate_on_submit():
        try:
            # Verificar si el usuario o email ya existen
            usuario_existente = Usuario.query.filter(
                (Usuario.username == form.username.data) | 
                (Usuario.email == form.email.data)
            ).first()
            
            if usuario_existente:
                if usuario_existente.username == form.username.data:
                    flash('El nombre de usuario ya está en uso. Elige otro.', 'error')
                else:
                    flash('El email ya está registrado en el sistema.', 'error')
                return render_template('admin/directivos_nuevo.html', form=form)
            
            # Crear nuevo usuario directivo
            directivo = Usuario(
                username=form.username.data,
                email=form.email.data,
                rol='directivo',
                nombre=form.nombre.data,
                apellido=form.apellido.data,
                activo=True,
                fecha_creacion=datetime.utcnow()
            )
            
            # Establecer contraseña
            directivo.set_password(form.password.data)
            
            # Agregar a la base de datos
            db.session.add(directivo)
            db.session.commit()
            
            flash(f'Directivo {form.nombre.data} {form.apellido.data} creado exitosamente.', 'success')
            return redirect(url_for('admin.directivos'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creando directivo: {e}")
            flash('Error al crear el directivo. Inténtalo de nuevo.', 'error')
    
    return render_template('admin/directivos_nuevo.html', form=form)

# ============================================
# GESTIÓN DE PADRES/ACUDIENTES
# ============================================

@admin_bp.route('/padres')
@login_required
def padres():
    """Lista de padres/acudientes"""
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    
    padres = Usuario.query.filter_by(rol='padre', activo=True).all()
    return render_template('admin/padres.html', padres=padres)

@admin_bp.route('/padres/nuevo', methods=['GET', 'POST'])
@login_required
def padres_nuevo():
    """Formulario para crear nuevo padre/acudiente"""
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    
    form = PadreForm()
    
    if form.validate_on_submit():
        try:
            # Verificar si el usuario o email ya existen
            usuario_existente = Usuario.query.filter(
                (Usuario.username == form.username.data) | 
                (Usuario.email == form.email.data)
            ).first()
            
            if usuario_existente:
                if usuario_existente.username == form.username.data:
                    flash('El nombre de usuario ya está en uso. Elige otro.', 'error')
                else:
                    flash('El email ya está registrado en el sistema.', 'error')
                return render_template('admin/padres_nuevo.html', form=form)
            
            # Crear nuevo usuario padre/acudiente
            padre = Usuario(
                username=form.username.data,
                email=form.email.data,
                rol='padre',
                nombre=form.nombre.data,
                apellido=form.apellido.data,
                activo=True,
                fecha_creacion=datetime.utcnow()
            )
            
            # Establecer contraseña
            padre.set_password(form.password.data)
            
            # Agregar a la base de datos
            db.session.add(padre)
            db.session.commit()
            
            flash(f'Padre/Acudiente {form.nombre.data} {form.apellido.data} creado exitosamente.', 'success')
            return redirect(url_for('admin.padres'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creando padre: {e}")
            flash('Error al crear el padre/acudiente. Inténtalo de nuevo.', 'error')
    
    return render_template('admin/padres_nuevo.html', form=form)

# ============================================
# GESTIÓN DE CURSOS/ASIGNATURAS
# ============================================

@admin_bp.route('/asignaturas')
@login_required
def asignaturas():
    """Lista de asignaturas/cursos"""
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    
    cursos = Curso.query.filter_by(activo=True).all()
    return render_template('admin/asignaturas.html', cursos=cursos)

@admin_bp.route('/asignaturas/nueva', methods=['GET', 'POST'])
@login_required
def asignaturas_nueva():
    """Formulario para crear nueva asignatura"""
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    
    form = CursoForm()
    
    # Cargar opciones de profesores dinámicamente
    docentes = Usuario.query.filter_by(rol='profesor', activo=True).all()
    form.profesor_id.choices = [('', 'Sin asignar')] + [(d.id, f"{d.nombre} {d.apellido}") for d in docentes]
    
    if form.validate_on_submit():
        try:
            # Verificar si el código ya existe
            curso_existente = Curso.query.filter_by(codigo=form.codigo.data).first()
            if curso_existente:
                flash('El código del curso ya existe. Elige otro.', 'error')
                return render_template('admin/asignaturas_nueva.html', form=form)
            
            # Crear nuevo curso
            curso = Curso(
                nombre=form.nombre.data,
                codigo=form.codigo.data,
                descripcion=form.descripcion.data,
                profesor_id=form.profesor_id.data if form.profesor_id.data else None,
                activo=True,
                fecha_creacion=datetime.utcnow()
            )
            
            # Agregar a la base de datos
            db.session.add(curso)
            db.session.commit()
            
            flash(f'Asignatura {form.nombre.data} creada exitosamente.', 'success')
            return redirect(url_for('admin.asignaturas'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creando curso: {e}")
            flash('Error al crear la asignatura. Inténtalo de nuevo.', 'error')
    
    return render_template('admin/asignaturas_nueva.html', form=form)

# ============================================
# RUTAS DE MENÚ GENERAL (SIN CAMBIOS)
# ============================================

@admin_bp.route('/agregar_usuario')
@login_required
def agregar_usuario():
    """Página principal para agregar usuarios"""
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/nuevo.html')

@admin_bp.route('/nuevo')
@login_required
def nuevo():
    """Página de opciones para crear nuevos elementos"""
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/nuevo.html')

# ============================================
# RUTAS EXISTENTES MANTENIDAS
# ============================================

@admin_bp.route('/evaluaciones')
@login_required
def evaluaciones():
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/evaluaciones.html')

@admin_bp.route('/reportes_rendimiento')
@login_required
def reportes_rendimiento():
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/reportes_rendimiento.html')

@admin_bp.route('/nivelaciones')
@login_required
def nivelaciones():
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/nivelaciones.html')

@admin_bp.route('/boletines')
@login_required
def boletines():
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/boletines.html')

@admin_bp.route('/asistencias')
@login_required
def asistencias():
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/asistencias.html')

@admin_bp.route('/observador')
@login_required
def observador():
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/observador.html')

@admin_bp.route('/reportes_convivencia')
@login_required
def reportes_convivencia():
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/reportes_convivencia.html')

@admin_bp.route('/tutorias')
@login_required
def tutorias():
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/tutorias.html')

@admin_bp.route('/agenda')
@login_required
def agenda():
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/agenda.html')

@admin_bp.route('/comunicados')
@login_required
def comunicados():
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/comunicados.html')

@admin_bp.route('/notificaciones')
@login_required
def notificaciones():
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/notificaciones.html')

@admin_bp.route('/contenidos')
@login_required
def contenidos():
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/contenidos.html')

@admin_bp.route('/materiales')
@login_required
def materiales():
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/materiales.html')

@admin_bp.route('/actividades')
@login_required
def actividades():
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/actividades.html')

@admin_bp.route('/foros')
@login_required
def foros():
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/foros.html')

@admin_bp.route('/periodos')
@login_required
def periodos():
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/periodos.html')

@admin_bp.route('/roles_permisos')
@login_required
def roles_permisos():
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/roles_permisos.html')

@admin_bp.route('/calendario_academico')
@login_required
def calendario_academico():
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/calendario_academico.html')

@admin_bp.route('/importar_exportar')
@login_required
def importar_exportar():
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/importar_exportar.html')

@admin_bp.route('/backup')
@login_required
def backup():
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/backup.html')

# ============================================
# RUTAS ADICIONALES PARA GESTIÓN AVANZADA
# ============================================

@admin_bp.route('/usuario/<int:user_id>')
@login_required
def ver_usuario(user_id):
    """Ver detalles de un usuario específico"""
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    
    usuario = Usuario.query.get_or_404(user_id)
    return render_template('admin/ver_usuario.html', usuario=usuario)

@admin_bp.route('/usuario/<int:user_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_usuario(user_id):
    """Editar un usuario existente"""
    if not verificar_admin():
        return redirect(url_for('admin.dashboard'))
    
    usuario = Usuario.query.get_or_404(user_id)
    
    # Seleccionar el formulario según el rol
    if usuario.rol == 'alumno':
        form = EstudianteForm(obj=usuario)
    elif usuario.rol == 'profesor':
        form = DocenteForm(obj=usuario)
    elif usuario.rol == 'directivo':
        form = DirectivoForm(obj=usuario)
    elif usuario.rol == 'padre':
        form = PadreForm(obj=usuario)
    else:
        flash('Tipo de usuario no válido para edición.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    if form.validate_on_submit():
        try:
            # Verificar si el username o email ya existen (excluyendo el usuario actual)
            usuario_existente = Usuario.query.filter(
                Usuario.id != user_id,
                (Usuario.username == form.username.data) | 
                (Usuario.email == form.email.data)
            ).first()
            
            if usuario_existente:
                if usuario_existente.username == form.username.data:
                    flash('El nombre de usuario ya está en uso. Elige otro.', 'error')
                else:
                    flash('El email ya está registrado en el sistema.', 'error')
                return render_template('admin/editar_usuario.html', form=form, usuario=usuario)
            
            # Actualizar campos básicos
            usuario.username = form.username.data
            usuario.email = form.email.data
            usuario.nombre = form.nombre.data
            usuario.apellido = form.apellido.data
            
            # Si se proporcionó nueva contraseña, actualizarla
            if form.password.data:
                usuario.set_password(form.password.data)
            
            db.session.commit()
            
            flash(f'Usuario {usuario.nombre} {usuario.apellido} actualizado exitosamente.', 'success')
            
            # Redirigir según el tipo de usuario
            if usuario.rol == 'alumno':
                return redirect(url_for('admin.estudiantes'))
            elif usuario.rol == 'profesor':
                return redirect(url_for('admin.docentes'))
            elif usuario.rol == 'directivo':
                return redirect(url_for('admin.directivos'))
            elif usuario.rol == 'padre':
                return redirect(url_for('admin.padres'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error actualizando usuario: {e}")
            flash('Error al actualizar el usuario. Inténtalo de nuevo.', 'error')
    
    return render_template('admin/editar_usuario.html', form=form, usuario=usuario)

@admin_bp.route('/usuario/<int:user_id>/toggle-status', methods=['POST'])
@login_required
def toggle_usuario_status(user_id):
    """Activar/desactivar un usuario"""
    if not verificar_admin():
        return jsonify({'error': 'Acceso no autorizado'}), 403
    
    try:
        usuario = Usuario.query.get_or_404(user_id)
        
        # No permitir desactivar al admin actual
        if usuario.id == current_user.id:
            return jsonify({'error': 'No puedes desactivar tu propia cuenta'}), 400
        
        usuario.activo = not usuario.activo
        db.session.commit()
        
        status_text = 'activado' if usuario.activo else 'desactivado'
        return jsonify({
            'success': True,
            'message': f'Usuario {status_text} exitosamente',
            'nuevo_status': usuario.activo
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error cambiando status de usuario: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@admin_bp.route('/usuario/<int:user_id>/eliminar', methods=['POST'])
@login_required
def eliminar_usuario(user_id):
    """Eliminar un usuario (soft delete)"""
    if not verificar_admin():
        return jsonify({'error': 'Acceso no autorizado'}), 403
    
    try:
        usuario = Usuario.query.get_or_404(user_id)
        
        # No permitir eliminar al admin actual
        if usuario.id == current_user.id:
            return jsonify({'error': 'No puedes eliminar tu propia cuenta'}), 400
        
        # Soft delete - marcar como inactivo
        usuario.activo = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Usuario {usuario.nombre} {usuario.apellido} eliminado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error eliminando usuario: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ============================================
# BÚSQUEDA Y FILTROS
# ============================================

@admin_bp.route('/buscar-usuarios')
@login_required
def buscar_usuarios():
    """Endpoint para búsqueda AJAX de usuarios"""
    if not verificar_admin():
        return jsonify({'error': 'Acceso no autorizado'}), 403
    
    query = request.args.get('q', '').strip()
    rol = request.args.get('rol', '')
    
    if len(query) < 2:
        return jsonify({'usuarios': []})
    
    try:
        # Construir query base
        usuarios_query = Usuario.query.filter(Usuario.activo == True)
        
        # Filtrar por rol si se especifica
        if rol and rol != 'todos':
            usuarios_query = usuarios_query.filter(Usuario.rol == rol)
        
        # Búsqueda en nombre, apellido, username o email
        usuarios_query = usuarios_query.filter(
            (Usuario.nombre.contains(query)) |
            (Usuario.apellido.contains(query)) |
            (Usuario.username.contains(query)) |
            (Usuario.email.contains(query))
        )
        
        usuarios = usuarios_query.limit(10).all()
        
        # Formatear resultados
        resultados = []
        for usuario in usuarios:
            resultados.append({
                'id': usuario.id,
                'nombre_completo': f"{usuario.nombre} {usuario.apellido}",
                'username': usuario.username,
                'email': usuario.email,
                'rol': usuario.rol,
                'activo': usuario.activo
            })
        
        return jsonify({'usuarios': resultados})
        
    except Exception as e:
        print(f"Error en búsqueda de usuarios: {e}")
        return jsonify({'error': 'Error en la búsqueda'}), 500

# ============================================
# ESTADÍSTICAS AVANZADAS
# ============================================

@admin_bp.route('/api/usuarios-por-rol')
@login_required
def usuarios_por_rol():
    """Estadísticas de usuarios por rol"""
    if not verificar_admin():
        return jsonify({'error': 'Acceso no autorizado'}), 403
    
    try:
        stats = db.session.query(
            Usuario.rol,
            func.count(Usuario.id).label('total')
        ).filter(Usuario.activo == True).group_by(Usuario.rol).all()
        
        data = {
            'labels': [stat.rol.title() for stat in stats],
            'data': [stat.total for stat in stats],
            'backgroundColor': [
                '#8E2DE2',  # admin
                '#10B981',  # profesor
                '#3B82F6',  # alumno
                '#F59E0B',  # directivo
                '#EF4444'   # padre
            ]
        }
        
        return jsonify(data)
        
    except Exception as e:
        print(f"Error obteniendo estadísticas por rol: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@admin_bp.route('/api/usuarios-recientes/<int:dias>')
@login_required
def usuarios_recientes(dias):
    """Usuarios registrados en los últimos N días"""
    if not verificar_admin():
        return jsonify({'error': 'Acceso no autorizado'}), 403
    
    try:
        fecha_limite = datetime.now() - timedelta(days=dias)
        
        usuarios = Usuario.query.filter(
            Usuario.fecha_creacion >= fecha_limite,
            Usuario.activo == True
        ).order_by(Usuario.fecha_creacion.desc()).all()
        
        resultados = []
        for usuario in usuarios:
            resultados.append({
                'id': usuario.id,
                'nombre': f"{usuario.nombre} {usuario.apellido}",
                'rol': usuario.rol,
                'email': usuario.email,
                'fecha_creacion': usuario.fecha_creacion.strftime('%Y-%m-%d %H:%M')
            })
        
        return jsonify({'usuarios': resultados})
        
    except Exception as e:
        print(f"Error obteniendo usuarios recientes: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500