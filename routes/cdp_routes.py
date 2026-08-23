"""
Rutas de Casa de Paz (CDP): /cdp/<uuid:id>/...
"""
from flask import Blueprint, render_template, request, session
from utils.auth import login_required, role_required, owner_required
from services.cdp_service import process_reporte, get_perfil_data
from database import get_db_connection

cdp_bp = Blueprint('cdp', __name__, url_prefix='/cdp')


@cdp_bp.route('/<uuid:id>/dashboard')
@login_required
@role_required("cdp")
@owner_required("id")
def dashboard(id):
    """Dashboard del CDP - solo accesible por el usuario dueño del ID."""
    usuario = session.get("usuario")
    return render_template('index.html', usuario=usuario)


@cdp_bp.route('/<uuid:id>/generar_reporte', methods=['GET', 'POST'])
@login_required
@role_required("cdp")
@owner_required("id")
def generar_reporte(id):
    """Generar reporte - solo accesible por el CDP dueño del ID."""
    if request.method == 'POST':
        result = process_reporte(
            anfitrion=request.form['anfitrion'],
            ninos=request.form['ninos'],
            regulares=request.form['regulares'],
            visitas=request.form['visitas'],
            comprometidos=request.form['comprometidos'],
            asistencia=request.form['asistencia'],
            reconciliaciones=request.form['reconciliaciones'],
            confesiones=request.form['confesiones'],
            cesta=request.form['cesta'],
            fecha=request.form['fecha'],
            horaini=request.form['horaini'],
            horafin=request.form['horafin'],
            tema=request.form['tema'],
            observaciones=request.form['observaciones'],
            ofrendas=request.form['ofrendas'],
        )

    usuario = session.get("usuario")
    return render_template('generar_reporte.html', usuario=usuario)


@cdp_bp.route('/<uuid:id>/perfil', methods=['GET', 'POST'])
@login_required
@role_required("cdp")
@owner_required("id")
def perfil(id):
    """Perfil del CDP - solo accesible por el usuario dueño del ID."""
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
@cdp_bp.route('/generar_reporte')
def generar_reporte_legacy():
    """Ruta legacy - redirige a la nueva ruta dinámica."""
    from flask import redirect, url_for
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("auth.login"))
    return redirect(url_for('cdp.generar_reporte', id=usuario_id), code=301)
