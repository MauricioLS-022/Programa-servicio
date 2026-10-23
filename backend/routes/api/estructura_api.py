"""
routes/api/estructura_api.py - Endpoints REST de estructura ministerial (redes, casas de paz, líderes).
"""
from flask import request, jsonify, session
from database import get_db_connection
from services.dashboard_service import get_supervisor_red_id
import db_queries
from services.cdp_service import (
    get_casas_sin_reporte_7d,
    get_cdp_detalle,
    crear_cdp_servicio,
    actualizar_cdp_servicio,
    toggle_cdp_servicio,
    eliminar_cdp_servicio,
    get_lideres_cdp_disponibles_servicio,
    obtener_cdps_para_select
)
from services.leader_service import (
    crear_red_servicio,
    obtener_red_servicio,
    actualizar_red_servicio,
    toggle_red_servicio,
    eliminar_red_servicio,
    get_supervisores_disponibles_servicio,
    crear_lider_servicio,
    obtener_lider_servicio,
    actualizar_lider_servicio,
    toggle_lider_servicio,
    eliminar_lider_servicio
)
from .base import api_bp, _serialize_item


@api_bp.route('/redes', methods=['GET'])
def api_get_redes():
    """Listado de redes ministeriales con supervisores asignados."""
    usuario_id = session.get("usuario_id")
    rol = session.get("rol")
    if not usuario_id:
        return jsonify({"error": "No autenticado"}), 401

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                query = """
                    SELECT r.id, r.nombre, r.is_active, r.supervisor_id,
                           CONCAT(COALESCE(u.nombre, ''), ' ', COALESCE(u.apellido, '')) AS supervisor_nombre,
                           u.username AS supervisor_username,
                           (SELECT COUNT(*) FROM cdp c WHERE c.red_id = r.id) AS total_casas
                    FROM red r
                    LEFT JOIN usuario u ON r.supervisor_id = u.id
                """
                params = []
                if rol == 'supervisor':
                    sup_red = get_supervisor_red_id(usuario_id)
                    if not sup_red:
                        return jsonify({"redes": []}), 200
                    query += " WHERE r.id = %s"
                    params.append(sup_red)
                query += " ORDER BY r.nombre ASC"
                cur.execute(query, params)
                redes = cur.fetchall() or []
                return jsonify({"redes": _serialize_item(redes)}), 200
        finally:
            conn.close()
    else:
        from mock_data import get_redes_demo
        demo_redes = get_redes_demo()
        if rol == 'supervisor':
            sup_red = get_supervisor_red_id(usuario_id) or 1
            demo_redes = [r for r in demo_redes if r.get('id') == sup_red]
        return jsonify({"redes": _serialize_item(demo_redes)}), 200


@api_bp.route('/redes', methods=['POST'])
def api_crear_red():
    """Creación de una nueva red ministerial."""
    if not session.get("usuario_id"):
        return jsonify({"error": "No autenticado"}), 401
    if session.get("rol") != 'admin':
        return jsonify({"error": "Acceso restringido a administradores"}), 403

    data = request.get_json(silent=True) or request.form.to_dict() or {}
    ok, mensaje = crear_red_servicio(data)
    if ok:
        return jsonify({"success": True, "message": mensaje}), 201
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/redes/<int:red_id>', methods=['GET'])
def api_get_red_detalle(red_id):
    """Consulta de datos de una red específica para edición."""
    if not session.get("usuario_id"):
        return jsonify({"error": "No autenticado"}), 401
    red_data = obtener_red_servicio(red_id)
    if not red_data:
        return jsonify({"error": "Red no encontrada"}), 404
    return jsonify({"red": _serialize_item(red_data)}), 200


@api_bp.route('/redes/<int:red_id>', methods=['PUT', 'POST'])
def api_editar_red(red_id):
    """Edición de nombre o supervisor de una red."""
    if not session.get("usuario_id"):
        return jsonify({"error": "No autenticado"}), 401
    if session.get("rol") != 'admin':
        return jsonify({"error": "Acceso restringido a administradores"}), 403

    data = request.get_json(silent=True) or request.form.to_dict() or {}
    ok, mensaje = actualizar_red_servicio(red_id, data)
    if ok:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/redes/<int:red_id>/toggle', methods=['POST'])
def api_toggle_red(red_id):
    """Alterna estado activa/pausada con propagación jerárquica."""
    if not session.get("usuario_id"):
        return jsonify({"error": "No autenticado"}), 401
    if session.get("rol") != 'admin':
        return jsonify({"error": "Acceso restringido a administradores"}), 403

    ok, mensaje = toggle_red_servicio(red_id)
    if ok:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/redes/<int:red_id>', methods=['DELETE'])
def api_eliminar_red(red_id):
    """Eliminación defensiva de una red ministerial."""
    if not session.get("usuario_id"):
        return jsonify({"error": "No autenticado"}), 401
    if session.get("rol") != 'admin':
        return jsonify({"error": "Acceso restringido a administradores"}), 403

    ok, mensaje = eliminar_red_servicio(red_id)
    if ok:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/casas_de_paz', methods=['GET'])
def api_get_casas_de_paz():
    """Listado de Casas de Paz con estado de cumplimiento semanal y filtros."""
    usuario_id = session.get("usuario_id")
    rol = session.get("rol")
    if not usuario_id:
        return jsonify({"error": "No autenticado"}), 401

    red_id_arg = request.args.get('red_id', '').strip()
    search = request.args.get('q', '').strip()
    filtro = request.args.get('filtro', '').strip().lower()

    target_red_id = red_id_arg
    if rol == 'supervisor':
        sup_red = get_supervisor_red_id(usuario_id)
        if not sup_red:
            return jsonify({"casas": [], "sin_reporte_7d_ids": []}), 200
        if red_id_arg and str(red_id_arg) != str(sup_red):
            return jsonify({"error": "No autorizado para consultar Casas de Paz de otra red"}), 403
        target_red_id = str(sup_red)

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                query = """
                    SELECT c.id, c.codigo, c.red_id, c.anfitrion, c.direccion, c.telefono,
                           c.is_active, r.nombre AS red_nombre,
                           (SELECT COUNT(*) FROM lider l WHERE l.cdp_id = c.id AND l.is_active = 1) AS total_lideres
                    FROM cdp c
                    JOIN red r ON c.red_id = r.id
                    WHERE 1=1
                """
                params = []
                if target_red_id:
                    query += " AND c.red_id = %s"
                    params.append(target_red_id)
                if search:
                    query += " AND (c.codigo LIKE %s OR c.anfitrion LIKE %s OR c.direccion LIKE %s)"
                    term = f"%{search}%"
                    params.extend([term, term, term])
                if filtro == 'activas':
                    query += " AND c.is_active = 1"
                elif filtro == 'pausadas':
                    query += " AND c.is_active = 0"

                query += " ORDER BY c.codigo ASC"
                cur.execute(query, params)
                casas = cur.fetchall() or []

                try:
                    sin_rep_ids = get_casas_sin_reporte_7d(int(target_red_id) if target_red_id else None)
                except Exception:
                    sin_rep_ids = []

                for c in casas:
                    c['sin_reporte_7d'] = c['id'] in sin_rep_ids

                if filtro == 'pendientes_7d':
                    casas = [c for c in casas if c['id'] in sin_rep_ids]

                return jsonify({
                    "casas": _serialize_item(casas),
                    "total": len(casas),
                    "sin_reporte_7d_ids": sin_rep_ids
                }), 200
        finally:
            conn.close()
    else:
        from mock_data import get_casas_demo
        casas = get_casas_demo()
        if target_red_id:
            casas = [c for c in casas if str(c.get('red_id', '')) == str(target_red_id)]
        return jsonify({
            "casas": _serialize_item(casas),
            "total": len(casas),
            "sin_reporte_7d_ids": []
        }), 200


@api_bp.route('/casas_de_paz/<int:cdp_id>', methods=['GET'])
def api_get_cdp_detalle(cdp_id):
    """Retorna la ficha técnica y auditoría completa de una Casa de Paz."""
    usuario_id = session.get("usuario_id")
    rol = session.get("rol")
    if not usuario_id:
        return jsonify({"error": "No autenticado"}), 401

    cdp = get_cdp_detalle(cdp_id)
    if not cdp:
        return jsonify({"error": "Casa de Paz no encontrada"}), 404

    # Aislamiento territorial para supervisores
    if rol == 'supervisor':
        sup_red = get_supervisor_red_id(usuario_id)
        if not sup_red or str(cdp.get('red_id')) != str(sup_red):
            return jsonify({"error": "No autorizado para consultar esta Casa de Paz"}), 403

    return jsonify({"cdp": _serialize_item(cdp)}), 200


@api_bp.route('/casas_de_paz', methods=['POST'])
def api_crear_cdp():
    """Creación de una nueva Casa de Paz."""
    if not session.get("usuario_id"):
        return jsonify({"error": "No autenticado"}), 401
    if session.get("rol") != 'admin':
        return jsonify({"error": "Acceso restringido a administradores"}), 403

    data = request.get_json(silent=True) or request.form.to_dict() or {}
    ok, mensaje = crear_cdp_servicio(data)
    if ok:
        return jsonify({"success": True, "message": mensaje}), 201
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/casas_de_paz/<int:cdp_id>', methods=['PUT', 'POST'])
def api_editar_cdp(cdp_id):
    """Edición de datos de una Casa de Paz existente."""
    if not session.get("usuario_id"):
        return jsonify({"error": "No autenticado"}), 401
    if session.get("rol") != 'admin':
        return jsonify({"error": "Acceso restringido a administradores"}), 403

    data = request.get_json(silent=True) or request.form.to_dict() or {}
    ok, mensaje = actualizar_cdp_servicio(cdp_id, data)
    if ok:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/casas_de_paz/<int:cdp_id>/toggle', methods=['POST'])
def api_toggle_cdp(cdp_id):
    """Alterna estado activa/pausada de una Casa de Paz."""
    if not session.get("usuario_id"):
        return jsonify({"error": "No autenticado"}), 401
    if session.get("rol") != 'admin':
        return jsonify({"error": "Acceso restringido a administradores"}), 403

    ok, status, mensaje = toggle_cdp_servicio(cdp_id)
    if ok:
        return jsonify({"success": True, "status": status, "message": mensaje}), 200
    return jsonify({"success": False, "status": status, "error": mensaje}), 400


@api_bp.route('/casas_de_paz/<int:cdp_id>', methods=['DELETE'])
def api_eliminar_cdp(cdp_id):
    """Baja defensiva de una Casa de Paz."""
    if not session.get("usuario_id"):
        return jsonify({"error": "No autenticado"}), 401
    if session.get("rol") != 'admin':
        return jsonify({"error": "Acceso restringido a administradores"}), 403

    ok, categoria, mensaje = eliminar_cdp_servicio(cdp_id)
    if ok:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/lideres', methods=['GET'])
def api_get_lideres():
    """Directorio de líderes ministeriales paginado y filtrado."""
    usuario_id = session.get("usuario_id")
    rol = session.get("rol")
    if not usuario_id:
        return jsonify({"error": "No autenticado"}), 401

    search = request.args.get('q', '').strip()
    rol_filtro = request.args.get('rol', '').strip()
    red_id_arg = request.args.get('red_id', '').strip()
    cdp_id_arg = request.args.get('cdp_id', '').strip()
    page = max(request.args.get('page', 1, type=int), 1)
    per_page = min(max(request.args.get('per_page', 10, type=int), 1), 100)

    supervisor_red_id = None
    target_red_id = red_id_arg

    if rol == 'supervisor':
        sup_red = get_supervisor_red_id(usuario_id)
        if not sup_red:
            return jsonify({"lideres": [], "total": 0, "page": page, "pages": 1}), 200
        if red_id_arg and str(red_id_arg) != str(sup_red):
            return jsonify({"error": "No autorizado para consultar líderes fuera de su red asignada"}), 403
        supervisor_red_id = sup_red
        target_red_id = str(sup_red)

    conn = get_db_connection()
    if conn:
        try:
            lideres, total, redes, casas = db_queries.get_lideres(
                conn,
                search=search,
                rol=rol_filtro,
                red_id=target_red_id,
                cdp_id=cdp_id_arg,
                supervisor_red_id=supervisor_red_id,
                page=page,
                per_page=per_page
            )
            total_pages = max((total + per_page - 1) // per_page, 1) if total else 1
            return jsonify({
                "lideres": _serialize_item(lideres),
                "total": total,
                "page": page,
                "pages": total_pages,
                "per_page": per_page
            }), 200
        finally:
            conn.close()
    else:
        from mock_data import get_mock_lideres
        mock_lideres = get_mock_lideres()
        if target_red_id:
            mock_lideres = [l for l in mock_lideres if str(l.get('red_id', '')) == str(target_red_id)]
        total = len(mock_lideres)
        return jsonify({
            "lideres": _serialize_item(mock_lideres),
            "total": total,
            "page": 1,
            "pages": 1,
            "per_page": per_page
        }), 200


@api_bp.route('/lideres/<int:lider_id>', methods=['GET'])
def api_get_lider_detalle(lider_id):
    """Consulta de datos de un líder específico para edición."""
    if not session.get("usuario_id"):
        return jsonify({"error": "No autenticado"}), 401
    lider = obtener_lider_servicio(lider_id)
    if not lider:
        return jsonify({"error": "Líder no encontrado"}), 404
    return jsonify({"lider": _serialize_item(lider)}), 200


@api_bp.route('/lideres', methods=['POST'])
def api_crear_lider():
    """Registro de un nuevo líder ministerial."""
    if not session.get("usuario_id"):
        return jsonify({"error": "No autenticado"}), 401
    if session.get("rol") != 'admin':
        return jsonify({"error": "Acceso restringido a administradores"}), 403

    data = request.get_json(silent=True) or request.form.to_dict() or {}
    ok, mensaje = crear_lider_servicio(data)
    if ok:
        return jsonify({"success": True, "message": mensaje}), 201
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/lideres/<int:lider_id>', methods=['PUT', 'POST'])
def api_editar_lider(lider_id):
    """Actualización de un líder ministerial."""
    if not session.get("usuario_id"):
        return jsonify({"error": "No autenticado"}), 401
    if session.get("rol") != 'admin':
        return jsonify({"error": "Acceso restringido a administradores"}), 403

    data = request.get_json(silent=True) or request.form.to_dict() or {}
    ok, mensaje = actualizar_lider_servicio(lider_id, data)
    if ok:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/lideres/<int:lider_id>/toggle', methods=['POST'])
def api_toggle_lider(lider_id):
    """Alterna estado activo/pausado de un líder."""
    if not session.get("usuario_id"):
        return jsonify({"error": "No autenticado"}), 401
    if session.get("rol") != 'admin':
        return jsonify({"error": "Acceso restringido a administradores"}), 403

    ok, status, mensaje = toggle_lider_servicio(lider_id)
    if ok:
        return jsonify({"success": True, "status": status, "message": mensaje}), 200
    return jsonify({"success": False, "status": status, "error": mensaje}), 400


@api_bp.route('/lideres/<int:lider_id>', methods=['DELETE'])
def api_eliminar_lider(lider_id):
    """Eliminación defensiva de un líder con candado de historial."""
    if not session.get("usuario_id"):
        return jsonify({"error": "No autenticado"}), 401
    if session.get("rol") != 'admin':
        return jsonify({"error": "Acceso restringido a administradores"}), 403

    ok, categoria, mensaje = eliminar_lider_servicio(lider_id)
    if ok:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/estructura/selectores', methods=['GET'])
def api_get_estructura_selectores():
    """Retorna opciones para los selectores de formularios de redes y casas."""
    if not session.get("usuario_id"):
        return jsonify({"error": "No autenticado"}), 401

    cdp_id = request.args.get('cdp_id', type=int)
    supervisores = get_supervisores_disponibles_servicio()
    lideres_cdp = get_lideres_cdp_disponibles_servicio(cdp_id=cdp_id)
    cdps = obtener_cdps_para_select()

    conn = get_db_connection()
    redes = []
    if conn:
        try:
            with conn.cursor() as cur:
                redes = db_queries.get_todas_las_redes(cur)
        finally:
            conn.close()

    return jsonify({
        "supervisores": _serialize_item(supervisores or []),
        "lideres_cdp": _serialize_item(lideres_cdp or []),
        "casas_de_paz": _serialize_item(cdps or []),
        "redes": _serialize_item(redes or [])
    }), 200
