"""
Rutas de Líder de Casa de Paz: /lider_cdp/...
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.auth import login_required, role_required
from services.cdp_service import process_reporte, get_perfil_data, get_cdp_datos_usuario

lider_cdp_bp = Blueprint('lider_cdp', __name__, url_prefix='/lider_cdp')


@lider_cdp_bp.route('/dashboard')
@login_required
@role_required("lider_cdp", "cdp")
def dashboard():
    """Dashboard del Líder de CDP."""
    usuario = session.get("usuario")
    return render_template('index.html', usuario=usuario)


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


@lider_cdp_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
@role_required("lider_cdp", "cdp")
def perfil():
    """Perfil del Líder de CDP."""
    usuario = session.get("usuario")
    usuario_id = session.get("usuario_id")
    rol = session.get("rol")
    perfil_data = get_perfil_data(str(usuario_id))
    
    return render_template('perfil.html', usuario=usuario, rol=rol, perfil_data=perfil_data)

