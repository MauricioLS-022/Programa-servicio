"""
Rutas del administrador: /admin/...
"""
from flask import Blueprint, render_template, request, session
from utils.auth import login_required, role_required
from services.dashboard_service import get_dashboard_context, get_estructura_context
from services.user_service import get_usuarios_context
from services.leader_service import get_lideres_context
from services.report_service import get_reportes_context

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@login_required
@role_required("admin")
def dashboard():
    """Dashboard del administrador - acceso completo."""
    usuario_id = session.get("usuario_id")
    context = get_dashboard_context(usuario_id, is_supervisor=False, default_nivel='general')
    return render_template('dashboard_admin.html', **context)


@admin_bp.route('/estructura')
@login_required
@role_required("admin")
def estructura():
    usuario_id = session.get("usuario_id")
    context = get_estructura_context(usuario_id, is_supervisor=False)
    return render_template('estructura_admin.html', **context)


@admin_bp.route('/usuario')
@login_required
@role_required("admin")
def usuario():
    search = request.args.get('q', '').strip()
    rol = request.args.get('rol', '').strip().lower()
    page = max(request.args.get('page', 1, type=int), 1)
    context = get_usuarios_context(search=search, rol=rol, page=page)
    return render_template('usuarios_admin.html', **context)


@admin_bp.route('/usuario/crear')
@login_required
@role_required("admin")
def usuario_crear():
    return render_template('form_usuario.html', title='Usuarios', breadcrumb='Usuario', link='usuario', is_edit=False)


@admin_bp.route('/usuario/<id>/editar')
@login_required
@role_required("admin")
def usuario_editar(id):
    return render_template('form_usuario.html', title='Usuarios', breadcrumb='Usuario', link='usuario', recurso_id=id, is_edit=True)


@admin_bp.route('/reportes')
@login_required
@role_required("admin")
def reportes():
    search = request.args.get('q', '').strip()
    red_id = request.args.get('red_id', '').strip()
    cdp_id = request.args.get('cdp_id', '').strip()
    fecha_desde = request.args.get('fecha_desde', '').strip()
    fecha_hasta = request.args.get('fecha_hasta', '').strip()
    page = max(request.args.get('page', 1, type=int), 1)
    context = get_reportes_context(
        search=search, red_id=red_id, cdp_id=cdp_id,
        fecha_desde=fecha_desde, fecha_hasta=fecha_hasta, page=page
    )
    return render_template('reportes_admin.html', **context)


@admin_bp.route('/lider')
@login_required
@role_required("admin")
def lider():
    search = request.args.get('q', '').strip()
    rol = request.args.get('rol', '').strip()
    red_id = request.args.get('red_id', '').strip()
    cdp_id = request.args.get('cdp_id', '').strip()
    page = max(request.args.get('page', 1, type=int), 1)
    context = get_lideres_context(search, rol, red_id, cdp_id, page)
    return render_template('lider_admin.html', **context)


@admin_bp.route('/lider/crear')
@login_required
@role_required("admin")
def lider_crear():
    return render_template('form_lider.html', title='Líderes', breadcrumb='Lider', link='lider', is_edit=False)


@admin_bp.route('/lider/<id>/editar')
@login_required
@role_required("admin")
def lider_editar(id):
    return render_template('form_lider.html', title='Líderes', breadcrumb='Lider', link='lider', recurso_id=id, is_edit=True)


@admin_bp.route('/casa_de_paz/crear')
@login_required
@role_required("admin")
def casa_de_paz_crear():
    return render_template('form_cdp.html', title='Casas de Paz', breadcrumb='Casa de paz', link='casa_de_paz', is_edit=False)


@admin_bp.route('/casa_de_paz/<id>')
@login_required
@role_required("admin")
def casa_de_paz(id):
    return render_template('detalles_cdp.html', title='Detalles de Casa de Paz', breadcrumb='Casa de paz', link='casa_de_paz', recurso_id=id)


@admin_bp.route('/casa_de_paz/<id>/editar')
@login_required
@role_required("admin")
def casa_de_paz_editar(id):
    return render_template('form_cdp.html', title='Casas de Paz', breadcrumb='Casa de paz', link='casa_de_paz', recurso_id=id, is_edit=True)


@admin_bp.route('/red/crear')
@login_required
@role_required("admin")
def red_crear():
    return render_template('form_redes.html', title='Redes', breadcrumb='Red', link='red', is_edit=False)


@admin_bp.route('/red/<id>/editar')
@login_required
@role_required("admin")
def red_editar(id):
    return render_template('form_redes.html', title='Redes', breadcrumb='Red', link='red', recurso_id=id, is_edit=True)


@admin_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
@role_required("admin")
def perfil():
    """Perfil del administrador."""
    from database import get_db_connection
    
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
