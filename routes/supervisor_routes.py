"""
Rutas del supervisor: /supervisor/...
"""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from utils.auth import login_required, role_required
from services.dashboard_service import get_dashboard_context, get_estructura_context, get_supervisor_red_id
from services.leader_service import get_lideres_context
from services.report_service import get_reportes_context
from database import get_db_connection

supervisor_bp = Blueprint('supervisor', __name__, url_prefix='/supervisor')


@supervisor_bp.route('/dashboard')
@login_required
@role_required("supervisor")
def dashboard():
    """Dashboard del supervisor."""
    usuario_id = session.get("usuario_id")
    context = get_dashboard_context(usuario_id, is_supervisor=True, default_nivel='red')
    return render_template('dashboard_admin.html', **context)


@supervisor_bp.route('/estructura')
@login_required
@role_required("supervisor")
def estructura():
    """Estructura de la red del supervisor."""
    usuario_id = session.get("usuario_id")
    usuario = session.get("usuario")
    context = get_estructura_context(usuario_id, is_supervisor=True)
    return render_template('estructura_admin.html', usuario=usuario, **context)


@supervisor_bp.route('/reportes')
@login_required
@role_required("supervisor")
def reportes():
    """Reportes de la red del supervisor."""
    usuario_id = session.get("usuario_id")
    usuario = session.get("usuario")
    search = request.args.get('q', '').strip()
    cdp_id = request.args.get('cdp_id', '').strip()
    fecha_desde = request.args.get('fecha_desde', '').strip()
    fecha_hasta = request.args.get('fecha_hasta', '').strip()
    page = max(request.args.get('page', 1, type=int), 1)
    red_id = get_supervisor_red_id(usuario_id)
    context = get_reportes_context(
        search=search, red_id='', cdp_id=cdp_id,
        fecha_desde=fecha_desde, fecha_hasta=fecha_hasta,
        page=page, supervisor_red_id=red_id
    )
    return render_template('reportes_admin.html', usuario=usuario, **context)


@supervisor_bp.route('/lider')
@login_required
@role_required("supervisor")
def lider():
    """Líderes de la red del supervisor."""
    usuario_id = session.get("usuario_id")
    usuario = session.get("usuario")
    search = request.args.get('q', '').strip()
    rol = request.args.get('rol', '').strip()
    cdp_id = request.args.get('cdp_id', '').strip()
    page = max(request.args.get('page', 1, type=int), 1)
    red_id = get_supervisor_red_id(usuario_id)
    context = get_lideres_context(search, rol, '', cdp_id, page, supervisor_red_id=red_id)
    return render_template('lider_admin.html', usuario=usuario, **context)


@supervisor_bp.route('/casa_de_paz/<id>')
@login_required
@role_required("supervisor")
def casa_de_paz(id):
    """Detalle de una Casa de Paz para supervisor."""
    from services.cdp_service import get_cdp_detalle
    cdp = get_cdp_detalle(id)
    return render_template('detalles_cdp.html', title='Detalles de Casa de Paz', breadcrumb='Casa de paz', link='casa_de_paz', recurso_id=id, cdp=cdp)


@supervisor_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
@role_required("supervisor")
def perfil():
    """Perfil del supervisor con cambio de usuario y contraseña."""
    from services.cdp_service import get_perfil_data, cambiar_username, cambiar_password
    
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
        
        return redirect(url_for('supervisor.perfil'))

    perfil_data = get_perfil_data(str(usuario_id)) if usuario_id else {}
    return render_template('perfil.html', usuario=usuario, rol=rol, perfil_data=perfil_data)

