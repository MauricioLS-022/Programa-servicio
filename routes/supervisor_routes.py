"""
Rutas del supervisor: /supervisor/<uuid:id>/...
"""
from flask import Blueprint, render_template, session
from utils.auth import login_required, role_required, owner_required
from services.dashboard_service import get_dashboard_context
from database import get_db_connection

supervisor_bp = Blueprint('supervisor', __name__, url_prefix='/supervisor')


@supervisor_bp.route('/<uuid:id>/dashboard')
@login_required
@role_required("supervisor")
@owner_required("id")
def dashboard(id):
    """Dashboard del supervisor - solo accesible por el usuario dueño del ID."""
    context = get_dashboard_context(str(id), is_supervisor=True, default_nivel='red')
    return render_template('dashboard_admin.html', **context)


@supervisor_bp.route('/<uuid:id>/estructura')
@login_required
@role_required("supervisor")
@owner_required("id")
def estructura(id):
    """Estructura de la red del supervisor."""
    usuario = session.get("usuario")
    return render_template('estructura_admin.html', usuario=usuario)


@supervisor_bp.route('/<uuid:id>/reportes')
@login_required
@role_required("supervisor")
@owner_required("id")
def reportes(id):
    """Reportes de la red del supervisor."""
    usuario = session.get("usuario")
    return render_template('reportes_admin.html', usuario=usuario)


@supervisor_bp.route('/<uuid:id>/lider')
@login_required
@role_required("supervisor")
@owner_required("id")
def lider(id):
    """Líderes de la red del supervisor."""
    usuario = session.get("usuario")
    return render_template('lider_admin.html', usuario=usuario)


@supervisor_bp.route('/<uuid:id>/perfil', methods=['GET', 'POST'])
@login_required
@role_required("supervisor")
@owner_required("id")
def perfil(id):
    """Perfil del supervisor."""
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
@supervisor_bp.route('/dashboard')
def dashboard_legacy():
    """Ruta legacy - redirige a la nueva ruta dinámica."""
    from flask import redirect, url_for
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("auth.login"))
    return redirect(url_for('supervisor.dashboard', id=usuario_id), code=301)
