"""
Rutas de Casa de Paz (CDP): /cdp/<uuid:id>/...
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.auth import login_required, role_required, owner_required
from services.cdp_service import process_reporte, get_perfil_data, get_cdp_datos_usuario

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
@role_required('cdp')
@owner_required('id')
def generar_reporte(id):
    # Obtenemos directamente la cdp y sus líderes desde el servicio
    cdp, lideres = get_cdp_datos_usuario(str(id))
    
    if not cdp:
        flash('No se encontró una Casa de Paz asignada a este usuario.', 'danger')
        return redirect(url_for('cdp.dashboard', id=id))

    if request.method == 'POST':
        exito = process_reporte(cdp_id=cdp['id'], form_data=request.form)
        if exito:
            flash('Reporte guardado exitosamente.', 'success')
            return redirect(url_for('cdp.dashboard', id=id))
        else:
            flash('Error al guardar el reporte. Verifica los datos introducidos.', 'danger')

    # En el GET se renderiza el formulario pasando los datos
    return render_template('generar_reporte.html', cdp=cdp, lideres=lideres)


@cdp_bp.route('/<uuid:id>/perfil', methods=['GET', 'POST'])
@login_required
@role_required("cdp")
@owner_required("id")
def perfil(id):
    """Perfil del CDP - solo accesible por el usuario dueño del ID."""
    usuario = session.get("usuario")
    
    # Delegamos la lógica de base de datos al servicio
    perfil_data = get_perfil_data(str(id))
    
    # Si en el futuro manejas un POST aquí, puedes usar update_perfil(str(id), request.form.get(...))
    
    return render_template('perfil.html', usuario=usuario, perfil_data=perfil_data)


# Legacy route
@cdp_bp.route('/generar_reporte')
def generar_reporte_legacy():
    """Ruta legacy - redirige a la nueva ruta dinámica."""
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("auth.login"))
    return redirect(url_for('cdp.generar_reporte', id=usuario_id), code=301)