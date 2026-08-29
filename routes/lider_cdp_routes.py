"""
Rutas de Líder de Casa de Paz: /lider_cdp/...
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.auth import login_required, role_required
from services.cdp_service import (
    process_reporte,
    get_perfil_data,
    get_cdp_datos_usuario,
    get_lider_dashboard_data,
    actualizar_reporte,
    eliminar_reporte,
    cambiar_username,
    cambiar_password,
)

lider_cdp_bp = Blueprint('lider_cdp', __name__, url_prefix='/lider_cdp')


@lider_cdp_bp.route('/dashboard')
@login_required
@role_required("lider_cdp", "cdp")
def dashboard():
    """Dashboard del Líder de CDP con métricas, equipo e historial."""
    usuario = session.get("usuario")
    usuario_id = session.get("usuario_id")
    page = max(request.args.get('page', 1, type=int), 1)
    contexto = get_lider_dashboard_data(str(usuario_id) if usuario_id else None, page=page)
    return render_template('index.html', usuario=usuario, **contexto)


@lider_cdp_bp.route('/generar_reporte', methods=['GET', 'POST'])
@login_required
@role_required('lider_cdp', 'cdp')
def generar_reporte():
    usuario_id = session.get("usuario_id")
    cdp, lideres = get_cdp_datos_usuario(str(usuario_id))
    
    if not cdp:
        flash('No se encontró una Casa de Paz asignada a este usuario.', 'danger')
        return redirect(url_for('lider_cdp.dashboard'))

    if request.method == 'POST':
        exito = process_reporte(cdp_id=cdp['id'], form_data=request.form)
        if exito:
            flash('Reporte guardado exitosamente.', 'success')
            return redirect(url_for('lider_cdp.dashboard'))
        else:
            flash('Error al guardar el reporte. Verifica los datos introducidos.', 'danger')

    return render_template('generar_reporte.html', cdp=cdp, lideres=lideres)


@lider_cdp_bp.route('/reporte/<reporte_id>/editar', methods=['POST'])
@login_required
@role_required('lider_cdp', 'cdp')
def editar_reporte_route(reporte_id):
    """Procesa la actualización de un reporte desde el modal."""
    usuario_id = session.get("usuario_id")
    cdp, _ = get_cdp_datos_usuario(str(usuario_id))
    
    if not cdp:
        flash('No tienes una Casa de Paz asignada para editar reportes.', 'danger')
        return redirect(url_for('lider_cdp.dashboard'))

    exito, mensaje = actualizar_reporte(reporte_id, cdp['id'], request.form)
    if exito:
        flash(mensaje, 'success')
    else:
        flash(mensaje, 'danger')

    return redirect(url_for('lider_cdp.dashboard'))


@lider_cdp_bp.route('/reporte/<reporte_id>/eliminar', methods=['POST'])
@login_required
@role_required('lider_cdp', 'cdp')
def eliminar_reporte_route(reporte_id):
    """Procesa la eliminación de un reporte desde el modal de confirmación."""
    usuario_id = session.get("usuario_id")
    cdp, _ = get_cdp_datos_usuario(str(usuario_id))
    
    if not cdp:
        flash('No tienes una Casa de Paz asignada para eliminar reportes.', 'danger')
        return redirect(url_for('lider_cdp.dashboard'))

    exito, mensaje = eliminar_reporte(reporte_id, cdp['id'])
    if exito:
        flash(mensaje, 'success')
    else:
        flash(mensaje, 'danger')

    return redirect(url_for('lider_cdp.dashboard'))


@lider_cdp_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
@role_required("lider_cdp", "cdp")
def perfil():
    """Perfil del Líder de CDP con cambio de usuario y contraseña."""
    usuario = session.get("usuario")
    usuario_id = session.get("usuario_id")
    rol = session.get("rol")

    if request.method == 'POST':
        action = request.form.get('action', '')
        
        if action == 'cambiar_username':
            nuevo_username = request.form.get('nuevo_username', '').strip()
            exito, mensaje = cambiar_username(usuario_id, nuevo_username)
            if exito:
                session['usuario'] = nuevo_username
                flash(mensaje, 'success')
            else:
                flash(mensaje, 'danger')
        
        elif action == 'cambiar_password':
            password_actual = request.form.get('password_actual', '')
            password_nueva = request.form.get('password_nueva', '')
            password_confirmar = request.form.get('password_confirmar', '')
            
            if password_nueva != password_confirmar:
                flash('Las contraseñas nuevas no coinciden', 'danger')
            else:
                exito, mensaje = cambiar_password(usuario_id, password_actual, password_nueva)
                flash(mensaje, 'success' if exito else 'danger')
        
        return redirect(url_for('lider_cdp.perfil'))

    perfil_data = get_perfil_data(str(usuario_id)) if usuario_id else {}
    return render_template('perfil.html', usuario=usuario, rol=rol, perfil_data=perfil_data)
