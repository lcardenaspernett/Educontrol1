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
    if current_user.rol == 'admin':
        return render_template('admin/dashboard.html', usuario=current_user)
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
