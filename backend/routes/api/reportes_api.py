"""
routes/api/reportes_api.py - Endpoints REST para consulta y gestión de reportes ministeriales.
"""
from flask import request, jsonify, session
from database import get_db_connection
from services.dashboard_service import get_supervisor_red_id
import db_queries
from services.cdp_service import (
    process_reporte,
    actualizar_reporte,
    eliminar_reporte,
    get_cdp_datos_usuario
)
from .base import api_bp, _serialize_item


@api_bp.route('/reportes', methods=['GET'])
def api_get_reportes():
    """Listado paginado y filtrado de reportes con aislamiento defensivo por rol."""
    usuario_id = session.get("usuario_id")
    rol = session.get("rol")
    if not usuario_id:
        return jsonify({"error": "No autenticado"}), 401

    search = request.args.get('q', '').strip()
    fecha_desde = request.args.get('fecha_desde', '').strip()
    fecha_hasta = request.args.get('fecha_hasta', '').strip()
    page = max(request.args.get('page', 1, type=int), 1)
    per_page = min(max(request.args.get('per_page', 10, type=int), 1), 100)

    red_id_arg = request.args.get('red_id', '').strip()
    cdp_id_arg = request.args.get('cdp_id', '').strip()

    supervisor_red_id = None
    target_red_id = red_id_arg
    target_cdp_id = cdp_id_arg

    # Restricciones por rol (Anti-IDOR)
    if rol == 'supervisor':
        sup_red = get_supervisor_red_id(usuario_id)
        if not sup_red:
            return jsonify({"reportes": [], "total": 0, "page": page, "pages": 1, "per_page": per_page}), 200
        if red_id_arg and str(red_id_arg) != str(sup_red):
            return jsonify({"error": "No autorizado para consultar reportes fuera de su red asignada"}), 403
        supervisor_red_id = sup_red
        target_red_id = str(sup_red)
    elif rol in ('lider_cdp', 'cdp'):
        cdp, _ = get_cdp_datos_usuario(str(usuario_id))
        if not cdp:
            return jsonify({"reportes": [], "total": 0, "page": page, "pages": 1, "per_page": per_page}), 200
        if cdp_id_arg and str(cdp_id_arg) != str(cdp['id']):
            return jsonify({"error": "No autorizado para consultar reportes de otra Casa de Paz"}), 403
        target_cdp_id = str(cdp['id'])

    conn = get_db_connection()
    if conn:
        try:
            reportes, total, redes, casas = db_queries.get_reportes(
                conn,
                search=search,
                red_id=target_red_id,
                cdp_id=target_cdp_id,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                supervisor_red_id=supervisor_red_id,
                page=page,
                per_page=per_page
            )
            total_pages = max((total + per_page - 1) // per_page, 1) if total else 1
            return jsonify({
                "reportes": _serialize_item(reportes),
                "total": total,
                "page": page,
                "pages": total_pages,
                "per_page": per_page
            }), 200
        finally:
            conn.close()
    else:
        # Modo demo / fallback testing
        from mock_data import get_mock_reportes
        mock_reps = get_mock_reportes()
        if target_red_id:
            mock_reps = [r for r in mock_reps if str(r.get('red_id', '')) == str(target_red_id)]
        if target_cdp_id:
            mock_reps = [r for r in mock_reps if str(r.get('cdp_id', '')) == str(target_cdp_id)]
        total = len(mock_reps)
        return jsonify({
            "reportes": _serialize_item(mock_reps),
            "total": total,
            "page": 1,
            "pages": 1,
            "per_page": per_page
        }), 200


@api_bp.route('/reportes', methods=['POST'])
def api_crear_reporte():
    """Registro de reporte con cálculo automático y validación ministerial."""
    usuario_id = session.get("usuario_id")
    rol = session.get("rol")
    if not usuario_id:
        return jsonify({"error": "No autenticado"}), 401

    data = request.get_json(silent=True) or request.form.to_dict() or {}

    cdp_id = None
    if rol in ('lider_cdp', 'cdp'):
        cdp, _ = get_cdp_datos_usuario(str(usuario_id))
        if not cdp:
            return jsonify({"error": "No tienes una Casa de Paz asignada"}), 403
        cdp_id = cdp['id']
    elif rol == 'admin':
        cdp_id_raw = data.get('cdp_id')
        if not cdp_id_raw:
            return jsonify({"error": "cdp_id es obligatorio para administradores"}), 400
        try:
            cdp_id = int(cdp_id_raw)
        except (ValueError, TypeError):
            return jsonify({"error": "cdp_id no válido"}), 400
    else:
        return jsonify({"error": "Rol no autorizado para generar reportes"}), 403

    res = process_reporte(cdp_id=cdp_id, form_data=data)
    exito = res[0] if isinstance(res, (tuple, list)) else bool(res)
    mensaje = res[1] if isinstance(res, (tuple, list)) and len(res) > 1 else (
        'Reporte guardado exitosamente.' if exito else 'Error al procesar el reporte.'
    )

    if exito:
        return jsonify({"success": True, "message": mensaje, "cdp_id": cdp_id}), 201
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/reportes/<string:reporte_id>', methods=['PUT', 'POST'])
def api_actualizar_reporte(reporte_id):
    """Actualización de un reporte existente perteneciente a la Casa de Paz."""
    usuario_id = session.get("usuario_id")
    rol = session.get("rol")
    if not usuario_id:
        return jsonify({"error": "No autenticado"}), 401

    data = request.get_json(silent=True) or request.form.to_dict() or {}

    cdp_id = None
    if rol in ('lider_cdp', 'cdp'):
        cdp, _ = get_cdp_datos_usuario(str(usuario_id))
        if not cdp:
            return jsonify({"error": "No tienes una Casa de Paz asignada"}), 403
        cdp_id = cdp['id']
    elif rol == 'admin':
        cdp_id = data.get('cdp_id') or 1
    elif rol == 'supervisor':
        cdp_id = data.get('cdp_id')
        if not cdp_id:
            return jsonify({"error": "cdp_id requerido para supervisores"}), 400
    else:
        return jsonify({"error": "No autorizado"}), 403

    exito, mensaje = actualizar_reporte(reporte_id, cdp_id, data)
    if exito:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/reportes/<string:reporte_id>', methods=['DELETE'])
def api_eliminar_reporte(reporte_id):
    """Eliminación segura de reporte con control de permisos."""
    usuario_id = session.get("usuario_id")
    rol = session.get("rol")
    if not usuario_id:
        return jsonify({"error": "No autenticado"}), 401

    cdp_id = None
    if rol in ('lider_cdp', 'cdp'):
        cdp, _ = get_cdp_datos_usuario(str(usuario_id))
        if not cdp:
            return jsonify({"error": "No tienes una Casa de Paz asignada"}), 403
        cdp_id = cdp['id']
    elif rol in ('admin', 'supervisor'):
        cdp_id = request.args.get('cdp_id', type=int) or 1
    else:
        return jsonify({"error": "No autorizado"}), 403

    exito, mensaje = eliminar_reporte(reporte_id, cdp_id)
    if exito:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "error": mensaje}), 400
