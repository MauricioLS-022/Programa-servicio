"""
routes/api/estructura_api.py - Endpoints REST de estructura ministerial (redes, casas de paz, líderes).
"""
from flask import request, jsonify, session
from database import get_db_connection
from services.dashboard_service import get_supervisor_red_id
import db_queries
from services.cdp_service import get_casas_sin_reporte_7d
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
                           u.username AS supervisor_username
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

                # Obtener IDs de casas sin reporte en los últimos 7 días
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
