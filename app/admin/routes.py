from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Usuario, db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

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
