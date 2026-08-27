"""
Rutas del supervisor: /supervisor/...
"""
from flask import Blueprint, render_template, request, session
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


@supervisor_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
@role_required("supervisor")
def perfil():
    """Perfil del supervisor."""
    usuario = session.get("usuario")
    rol = session.get("rol")
    connect = get_db_connection()
    if connect:
        try:
            C = connect.cursor()
        except Exception as e:
            print(f"[DB] Error perfil: {e}")
        finally:
            connect.close()
    
    return render_template('perfil.html', usuario=usuario, rol=rol)
