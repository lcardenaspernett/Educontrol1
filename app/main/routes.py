from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Usuario, db
from app.forms import UsuarioForm

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """Página principal"""
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal"""
    return render_template('dashboard.html')

@main_bp.route('/profile')
@login_required
def profile():
    """Página de perfil del usuario"""
    return render_template('profile.html')

@main_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Editar perfil del usuario"""
    form = UsuarioForm(obj=current_user)
    
    if form.validate_on_submit():
        try:
            # Actualizar datos del usuario
            current_user.nombre = form.nombre.data
            current_user.apellido = form.apellido.data
            current_user.email = form.email.data
            current_user.telefono = form.telefono.data
            
            if form.password.data:
                current_user.set_password(form.password.data)
            
            db.session.commit()
            flash('Perfil actualizado exitosamente', 'success')
            return redirect(url_for('main.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar el perfil', 'error')
            
    return render_template('edit_profile.html', form=form)
