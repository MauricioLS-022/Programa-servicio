"""
Rutas del administrador: /admin/...
"""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from database import get_db_connection
from db_queries import get_todas_las_redes, obtener_cdp_admin
from utils.auth import login_required, role_required
from services.dashboard_service import get_dashboard_context, get_estructura_context
from services.user_service import (
    get_usuarios_context,
    obtener_usuario_por_id,
    actualizar_usuario_admin,
    toggle_usuario_servicio,
)
from services.leader_service import (
    get_lideres_context,
    crear_nuevo_usuario,
    get_opciones_asignacion,
    get_supervisores_disponibles_servicio,
    crear_red_servicio,
    obtener_red_servicio,
    actualizar_red_servicio,
    toggle_red_servicio,
    eliminar_red_servicio,
    toggle_lider_servicio,
    obtener_lider_servicio,
    actualizar_lider_servicio,
    crear_lider_servicio,
)
from services.cdp_service import (
    crear_cdp_servicio,
    actualizar_cdp_servicio,
    eliminar_cdp_servicio,
    get_lideres_cdp_disponibles_servicio,
    toggle_cdp_servicio,
    actualizar_reporte,
)

try:
    from services.cdp_service import obtener_cdps_para_select
except ImportError:
    def obtener_cdps_para_select():
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT c.id, c.codigo, c.direccion, c.is_active, r.nombre AS red_nombre
                        FROM cdp c
                        LEFT JOIN red r ON c.red_id = r.id
                        WHERE c.is_active = 1
                        ORDER BY c.codigo ASC
                    """)
                    return cursor.fetchall() or []
            except Exception as e:
                print(f"[ERROR] Error al obtener CDPs para select: {e}")
                return []
            finally:
                conn.close()
        else:
            try:
                from mock_data import get_mock_casas
                return [c for c in get_mock_casas() if c.get('is_active', 1) == 1]
            except Exception:
                return []

    import services.cdp_service
    services.cdp_service.obtener_cdps_para_select = obtener_cdps_para_select

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


@admin_bp.route('/usuario/crear', methods=['GET', 'POST'])
@login_required
@role_required("admin")
def usuario_crear():
    usuario_data = None
    if request.method == 'POST':
        success, message = crear_nuevo_usuario(request.form)
        if success:
            flash(message, "success")
            return redirect(url_for('admin.usuario')) 
        else:
            flash(message, "danger")
            usuario_data = request.form
            
    redes_disponibles, cdps_disponibles = get_opciones_asignacion()
    return render_template(
        'form_usuario.html',
        title='Usuarios',
        breadcrumb='Usuario',
        link='usuario',
        is_edit=False,
        usuario_data=usuario_data,
        redes_disponibles=redes_disponibles,
        cdps_disponibles=cdps_disponibles,
    )

@admin_bp.route('/usuario/<id>/editar', methods=['GET', 'POST'])
@login_required
@role_required("admin")
def usuario_editar(id):
    usuario_data = obtener_usuario_por_id(id)
    if not usuario_data:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for('admin.usuario'))

    if request.method == 'POST':
        success, message = actualizar_usuario_admin(id, request.form)
        if success:
            flash(message, "success")
            return redirect(url_for('admin.usuario'))
        else:
            flash(message, "danger")
            usuario_data = {**usuario_data, **request.form.to_dict()}

    redes_disponibles, cdps_disponibles = get_opciones_asignacion(usuario_id=id)

    return render_template(
        'form_usuario.html',
        title='Usuarios',
        breadcrumb='Usuario',
        link='usuario',
        recurso_id=id,
        usuario_data=usuario_data,
        is_edit=True,
        redes_disponibles=redes_disponibles,
        cdps_disponibles=cdps_disponibles,
    )


@admin_bp.route('/usuario/<id>/toggle_estado', methods=['POST'])
@login_required
@role_required("admin")
def usuario_toggle_estado(id):
    ok, status, mensaje = toggle_usuario_servicio(id)
    if ok:
        flash(mensaje, 'success')
    else:
        flash(mensaje, 'error')

    if request.referrer:
        return redirect(request.referrer)
    try:
        return redirect(url_for('admin_routes.admin_usuarios'))
    except Exception:
        return redirect(url_for('admin.usuario'))


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


@admin_bp.route('/reporte/<reporte_id>/editar', methods=['POST'])
@login_required
@role_required("admin")
def reporte_editar(reporte_id):
    """Procesa la actualización de un reporte desde el modal de administración."""
    cdp_id = request.form.get('cdp_id')
    exito, mensaje = actualizar_reporte(reporte_id, cdp_id, request.form)
    if exito:
        flash(mensaje, 'success')
    else:
        flash(mensaje, 'danger')

    if request.referrer:
        return redirect(request.referrer)
    return redirect(url_for('admin.reportes'))


@admin_bp.route('/lider')
@admin_bp.route('/lideres')
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


@admin_bp.route('/lider/crear', methods=['GET', 'POST'])
@login_required
@role_required("admin")
def lider_crear():
    lider_data = None
    if request.method == 'POST':
        success, mensaje = crear_lider_servicio(request.form)
        if success:
            flash(mensaje, 'success')
            return redirect(url_for('admin.lider'))
        else:
            if 'inactiva' in mensaje.lower() or 'pausada' in mensaje.lower() or 'bloquead' in mensaje.lower():
                flash(mensaje, 'warning')
            else:
                flash(mensaje, 'danger')
            lider_data = request.form

    casas_de_paz = obtener_cdps_para_select()
    return render_template(
        'form_lider.html',
        title='Líderes',
        breadcrumb='Lider',
        link='lider',
        is_edit=False,
        lider=lider_data,
        casas_de_paz=casas_de_paz,
    )


@admin_bp.route('/lider/<int:id>/editar', methods=['GET', 'POST'])
@admin_bp.route('/lider/<id>/editar', methods=['GET', 'POST'])
@login_required
@role_required("admin")
def lider_editar(id):
    try:
        id_int = int(id)
    except (ValueError, TypeError):
        flash("Líder no encontrado.", "danger")
        return redirect(url_for('admin.lider'))

    lider_data = obtener_lider_servicio(id_int)
    if not lider_data:
        flash("El líder no existe o ya fue eliminado.", "warning")
        return redirect(url_for('admin.lider'))

    if request.method == 'POST':
        success, mensaje = actualizar_lider_servicio(id_int, request.form)
        if success:
            flash(mensaje, 'success')
            return redirect(url_for('admin.lider'))
        else:
            if 'inactiva' in mensaje.lower() or 'pausada' in mensaje.lower() or 'bloquead' in mensaje.lower():
                flash(mensaje, 'warning')
            else:
                flash(mensaje, 'danger')
            lider_data = {**lider_data, **request.form.to_dict()}

    casas_de_paz = obtener_cdps_para_select()
    return render_template(
        'form_lider.html',
        title='Líderes',
        breadcrumb='Lider',
        link='lider',
        recurso_id=id_int,
        is_edit=True,
        lider=lider_data,
        casas_de_paz=casas_de_paz,
    )


@admin_bp.route('/lider/<int:id>/eliminar', methods=['POST'])
@login_required
@role_required("admin")
def lider_eliminar(id):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT nombre, apellido FROM lider WHERE id = %s", (id,))
                lider_row = cursor.fetchone()
                if not lider_row:
                    flash("El líder no existe o ya fue eliminado.", "warning")
                    return redirect(url_for('admin.lider'))
                
                nombre_completo = f"{lider_row.get('nombre', '')} {lider_row.get('apellido', '')}".strip()
                cursor.execute("DELETE FROM lider WHERE id = %s", (id,))
            conn.commit()
            flash(f"Líder '{nombre_completo}' eliminado exitosamente.", "success")
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Error al eliminar líder: {e}")
            flash("Error al eliminar el líder de la base de datos.", "danger")
        finally:
            conn.close()
    else:
        flash("No se pudo conectar a la base de datos.", "danger")

    return redirect(url_for('admin.lider'))


@admin_bp.route('/lider/<id>/toggle_estado', methods=['POST'])
@login_required
@role_required("admin")
def lider_toggle_estado(id):
    ok, status, mensaje = toggle_lider_servicio(id)
    if ok:
        flash(mensaje, 'success')
    else:
        if status == 'bloqueada':
            flash(mensaje, 'warning')
        else:
            flash(mensaje, 'error')

    if request.referrer:
        return redirect(request.referrer)
    try:
        return redirect(url_for('admin_routes.admin_lideres'))
    except Exception:
        return redirect(url_for('admin.lider'))



@admin_bp.route('/casa_de_paz/crear', methods=['GET', 'POST'])
@login_required
@role_required("admin")
def casa_de_paz_crear():

    if request.method == 'POST':
        success, mensaje = crear_cdp_servicio(request.form)

        if success:
            flash(mensaje, 'success')
            return redirect(url_for('admin.estructura'))
        else:
            flash(mensaje, 'danger')

    conn = get_db_connection()
    redes = []
    if conn:
        with conn.cursor() as cursor:
            redes = get_todas_las_redes(cursor)
        conn.close()
        
    lideres_disponibles = get_lideres_cdp_disponibles_servicio()

    return render_template(
        'form_cdp.html', 
        title='Casas de Paz', 
        breadcrumb='Casa de paz', 
        link='casa_de_paz',
        redes=redes, 
        lideres_disponibles=lideres_disponibles,
        is_edit=False
    )


@admin_bp.route('/casa_de_paz/<id>')
@login_required
@role_required("admin")
def casa_de_paz(id):
    from services.cdp_service import get_cdp_detalle
    cdp = get_cdp_detalle(id)
    return render_template('detalles_cdp.html', title='Detalles de Casa de Paz', breadcrumb='Casa de paz', link='casa_de_paz', recurso_id=id, cdp=cdp)


@admin_bp.route('/casa_de_paz/<id>/editar', methods=['GET', 'POST'])
@login_required
@role_required("admin")
def casa_de_paz_editar(id):

    conn = get_db_connection()
    cdp_data = None
    redes = []

    if conn:
        with conn.cursor() as cursor:
            cdp_data = obtener_cdp_admin(cursor, id)
            redes = get_todas_las_redes(cursor)
        conn.close()

    if not cdp_data:
        flash("La Casa de Paz no existe.", 'danger')
        return redirect(url_for('admin.estructura'))

    if request.method == 'POST':
        success, mensaje = actualizar_cdp_servicio(id, request.form)
        if success:
            flash(mensaje, 'success')
            return redirect(url_for('admin.estructura'))
        else:
            if 'red' in mensaje.lower() and ('pausa' in mensaje.lower() or 'inactiv' in mensaje.lower() or 'bloquead' in mensaje.lower()):
                flash(mensaje, 'warning')
            else:
                flash(mensaje, 'danger')

    lideres_disponibles = get_lideres_cdp_disponibles_servicio(cdp_id=id)

    return render_template(
        'form_cdp.html', 
        title='Casas de Paz', 
        breadcrumb='Casa de paz', 
        link='casa_de_paz', 
        recurso_id=id, 
        cdp=cdp_data,
        redes=redes, 
        lideres_disponibles=lideres_disponibles,
        is_edit=True
    )

@admin_bp.route('/casa_de_paz/<id>/eliminar', methods=['POST'])
@login_required
@role_required('admin')
def casa_de_paz_eliminar(id):
    exito, categoria, mensaje = eliminar_cdp_servicio(id)
    flash(mensaje, categoria)
    return redirect(url_for('admin.estructura'))


@admin_bp.route('/casa_de_paz/<id>/toggle_estado', methods=['POST'])
@login_required
@role_required("admin")
def casa_de_paz_toggle_estado(id):
    ok, status, mensaje = toggle_cdp_servicio(id)
    if ok:
        flash(mensaje, 'success')
    else:
        if status == 'bloqueada':
            flash(mensaje, 'warning')
        else:
            flash(mensaje, 'error')

    if request.referrer:
        return redirect(request.referrer)
    try:
        return redirect(url_for('admin_routes.admin_casa_de_paz'))
    except Exception:
        return redirect(url_for('admin.estructura'))


@admin_bp.route('/red/crear', methods=['GET', 'POST'])
@login_required
@role_required("admin")
def red_crear():
    if request.method == 'POST':
        success, message = crear_red_servicio(request.form)
        if success:
            flash(message, 'success')
            return redirect(url_for('admin.estructura'))
        else:
            flash(message, 'danger')

    supervisores_disponibles = get_supervisores_disponibles_servicio()
    return render_template(
        'form_redes.html',
        title='Redes',
        breadcrumb='Red',
        link='red',
        is_edit=False,
        supervisores_disponibles=supervisores_disponibles,
    )


@admin_bp.route('/red/<id>/editar', methods=['GET', 'POST'])
@login_required
@role_required("admin")
def red_editar(id):

    red_data = obtener_red_servicio(id)
    if not red_data:
        flash("Red no encontrada", "danger")
        return redirect(url_for('admin.estructura'))
    
    if request.method == 'POST':
        success, message = actualizar_red_servicio(id, request.form)
        if success:
            flash(message, 'success')
            return redirect(url_for('admin.estructura'))
        else:
            flash(message, 'danger')
        
    # Obtener supervisores disponibles + el supervisor actual de esta red (para que aparezca en el select)
    supervisores_disponibles = get_supervisores_disponibles_servicio()

    if red_data.get('supervisor_id'):
        # Si el supervisor actual no está en la lista de disponibles (porque ya está asignado a esta red), lo consultamos y lo incluimos
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, nombre, apellido, username FROM usuario WHERE id = %s", (red_data['supervisor_id'],))
                sup_actual = cursor.fetchone()

                if sup_actual and not any(s['id'] == sup_actual['id'] for s in supervisores_disponibles):
                    supervisores_disponibles.insert(0, sup_actual)  # Insertamos al inicio de la lista para que sea el seleccionado por defecto
            conn.close()

    return render_template(
        'form_redes.html', 
        title='Redes',
        breadcrumb='Red', 
        link='red', 
        recurso_id=id, 
        is_edit=True,
        red = red_data,
        supervisores_disponibles=supervisores_disponibles
    )

@admin_bp.route('/red/<int:id>/toggle_estado', methods=['POST'])
@login_required
@role_required("admin")
def red_toggle_estado(id):
    success, message = toggle_red_servicio(id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('admin.estructura'))


@admin_bp.route('/red/<int:id>/eliminar', methods=['POST'])
@login_required
@role_required("admin")
def red_eliminar(id):
    success, message = eliminar_red_servicio(id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('admin.estructura'))



@admin_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
@role_required("admin")
def perfil():
    """Perfil del administrador con cambio de usuario y contraseña."""
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
        
        return redirect(url_for('admin.perfil'))

    perfil_data = get_perfil_data(str(usuario_id)) if usuario_id else {}
    return render_template('perfil.html', usuario=usuario, rol=rol, perfil_data=perfil_data)

