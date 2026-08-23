"""
Rutas del administrador: /admin/<uuid:id>/...
"""
from flask import Blueprint, render_template, request, session
from utils.auth import login_required, role_required
from services.dashboard_service import get_dashboard_context

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/<uuid:id>/dashboard')
@login_required
@role_required("admin")
def dashboard(id):
    """Dashboard del administrador - acceso completo."""
    context = get_dashboard_context(str(id), is_supervisor=False, default_nivel='general')
    return render_template('dashboard_admin.html', **context)


@admin_bp.route('/<uuid:id>/estructura')
@login_required
@role_required("admin")
def estructura(id):
    return render_template('estructura_admin.html')


@admin_bp.route('/<uuid:id>/usuario')
@login_required
@role_required("admin")
def usuario(id):
    return render_template('usuarios_admin.html')


@admin_bp.route('/<uuid:id>/usuario/editar')
@login_required
@role_required("admin")
def usuario_editar(id):
    return render_template('form_usuario.html', title='Usuarios', breadcrumb='Usuario', link='usuario')


@admin_bp.route('/<uuid:id>/reportes')
@login_required
@role_required("admin")
def reportes(id):
    return render_template('reportes_admin.html')


@admin_bp.route('/<uuid:id>/lider')
@login_required
@role_required("admin")
def lider(id):
    return render_template('lider_admin.html')


@admin_bp.route('/<uuid:id>/lider/editar')
@login_required
@role_required("admin")
def lider_editar(id):
    return render_template('form_lider.html', title='Líderes', breadcrumb='Lider', link='lider')


@admin_bp.route('/<uuid:id>/casa_de_paz')
@login_required
@role_required("admin")
def casa_de_paz(id):
    return render_template('detalles_cdp.html', title='Detalles de Casa de Paz', breadcrumb='Casa de paz', link='casa_de_paz')


@admin_bp.route('/<uuid:id>/casa_de_paz/editar')
@login_required
@role_required("admin")
def casa_de_paz_editar(id):
    return render_template('form_cdp.html', title='Casas de Paz', breadcrumb='Casa de paz', link='casa_de_paz')


@admin_bp.route('/<uuid:id>/red/editar')
@login_required
@role_required("admin")
def red_editar(id):
    return render_template('form_redes.html', title='Redes', breadcrumb='Red', link='red')


@admin_bp.route('/<uuid:id>/perfil', methods=['GET', 'POST'])
@login_required
@role_required("admin")
def perfil(id):
    """Perfil del administrador."""
    from database import get_db_connection
    
    usuario = session.get("usuario")
    connect = get_db_connection()
    if connect:
        try:
            C = connect.cursor()
        except Exception as e:
            print(f"[DB] Error perfil: {e}")
        finally:
            connect.close()
    
    return render_template('perfil.html', usuario=usuario)


# Legacy route
@admin_bp.route('/dashboard')
def dashboard_legacy():
    """Ruta legacy - redirige a la nueva ruta dinámica."""
    from flask import redirect, url_for
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("auth.login"))
    return redirect(url_for('admin.dashboard', id=usuario_id), code=301)
