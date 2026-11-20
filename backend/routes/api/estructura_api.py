"""
routes/api/estructura_api.py - Endpoints REST de estructura ministerial (redes, casas de paz, líderes).
"""
from flask import request, jsonify, session
from database import get_db_connection
from services.dashboard_service import get_supervisor_red_id, mock_mode_enabled
from repositories import get_estructura_repository, get_lider_repository
from repositories.mock_repositories import NullEstructuraRepository, NullLiderRepository


def _db_unavailable_response():
    return jsonify({
        "success": False,
        "error": "Base de datos temporalmente no disponible. Intente nuevamente en unos segundos.",
        "code": "db_unavailable",
    }), 503
from services.cdp_service import (
    get_casas_sin_reporte_7d,
    get_cdp_datos_usuario,
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
from utils.auth import api_auth_required, api_role_required
from policies.access_policy import AccessPolicy, UserContext
from schemas import (
    parse_payload,
    RedCreateDTO,
    RedUpdateDTO,
    CdpCreateDTO,
    CdpUpdateDTO,
    LiderCreateDTO,
    LiderUpdateDTO,
)
from .base import api_bp, _serialize_item


@api_bp.route('/redes', methods=['GET'])
@api_role_required('admin', 'supervisor')
def api_get_redes():
    """Listado de redes ministeriales con supervisores asignados."""
    usuario_id = session.get("usuario_id")
    rol = session.get("rol")

    supervisor_red_id = None
    if rol == 'supervisor':
        sup_red = get_supervisor_red_id(usuario_id)
        if not sup_red:
            return jsonify({"redes": []}), 200
        supervisor_red_id = sup_red

    repo = get_estructura_repository()
    if isinstance(repo, NullEstructuraRepository):
        return _db_unavailable_response()
    redes = repo.list_redes(supervisor_red_id=supervisor_red_id)
    return jsonify({"redes": _serialize_item(redes)}), 200


@api_bp.route('/redes', methods=['POST'])
@api_role_required('admin')
def api_crear_red():
    """Creación de una nueva red ministerial."""
    raw_data = request.get_json(silent=True) or request.form.to_dict() or {}
    dto = parse_payload(RedCreateDTO, raw_data)
    ok, mensaje = crear_red_servicio(dto.to_service_dict())
    if ok:
        return jsonify({"success": True, "message": mensaje}), 201
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/redes/<int:red_id>', methods=['GET'])
@api_role_required('admin', 'supervisor')
def api_get_red_detalle(red_id):
    """Consulta de datos de una red específica para edición."""
    usuario_id = session.get("usuario_id")
    rol = session.get("rol")

    if rol == 'supervisor':
        sup_red = get_supervisor_red_id(usuario_id)
        user_ctx = UserContext(usuario_id=str(usuario_id), rol=rol, supervisor_red_id=sup_red)
        if not AccessPolicy.can_access_red(user_ctx, red_id):
            return jsonify({"error": "No autorizado para consultar esta red"}), 403

    red_data = obtener_red_servicio(red_id)
    if not red_data:
        return jsonify({"error": "Red no encontrada"}), 404
    return jsonify({"red": _serialize_item(red_data)}), 200


@api_bp.route('/redes/<int:red_id>', methods=['PUT', 'POST'])
@api_role_required('admin')
def api_editar_red(red_id):
    """Edición de nombre o supervisor de una red."""
    raw_data = request.get_json(silent=True) or request.form.to_dict() or {}
    dto = parse_payload(RedUpdateDTO, raw_data)
    ok, mensaje = actualizar_red_servicio(red_id, dto.to_service_dict())
    if ok:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/redes/<int:red_id>/toggle', methods=['POST'])
@api_role_required('admin')
def api_toggle_red(red_id):
    """Alterna estado activa/pausada con propagación jerárquica."""
    ok, mensaje = toggle_red_servicio(red_id)
    if ok:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/redes/<int:red_id>', methods=['DELETE'])
@api_role_required('admin')
def api_eliminar_red(red_id):
    """Eliminación defensiva de una red ministerial."""
    ok, mensaje = eliminar_red_servicio(red_id)
    if ok:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/casas_de_paz', methods=['GET'])
@api_auth_required
def api_get_casas_de_paz():
    """Listado de Casas de Paz con estado de cumplimiento semanal y filtros."""
    usuario_id = session.get("usuario_id")
    rol = session.get("rol")

    red_id_arg = request.args.get('red_id', '').strip()
    search = request.args.get('q', '').strip()
    filtro = request.args.get('filtro', '').strip().lower()

    target_red_id = red_id_arg
    own_cdp_id = None
    if rol == 'supervisor':
        sup_red = get_supervisor_red_id(usuario_id)
        if not sup_red:
            return jsonify({"casas": [], "total": 0, "sin_reporte_7d_ids": []}), 200
        user_ctx = UserContext(usuario_id=str(usuario_id), rol=rol, supervisor_red_id=sup_red)
        if red_id_arg and not AccessPolicy.can_access_red(user_ctx, red_id_arg):
            return jsonify({"error": "No autorizado para consultar Casas de Paz de otra red"}), 403
        target_red_id = str(sup_red)
    elif rol in ('lider_cdp', 'cdp'):
        cdp_propia, _ = get_cdp_datos_usuario(usuario_id)
        if not cdp_propia:
            return jsonify({"casas": [], "total": 0, "sin_reporte_7d_ids": []}), 200
        own_cdp_id = int(cdp_propia['id'])
        own_red_id = cdp_propia.get('red_id')
        if red_id_arg and own_red_id is not None and str(red_id_arg) != str(own_red_id):
            return jsonify({"error": "No autorizado para consultar Casas de Paz de otra red"}), 403
        target_red_id = str(own_red_id) if own_red_id is not None else ''

    repo = get_estructura_repository()
    if isinstance(repo, NullEstructuraRepository):
        return _db_unavailable_response()
    casas, sin_rep_ids = repo.list_casas_de_paz(
        red_id=target_red_id,
        search=search,
        filtro=filtro,
    )
    if own_cdp_id is not None:
        casas = [c for c in casas if str(c.get('id', '')) == str(own_cdp_id)]
        sin_rep_ids = [cid for cid in sin_rep_ids if str(cid) == str(own_cdp_id)]
    return jsonify({
        "casas": _serialize_item(casas),
        "total": len(casas),
        "sin_reporte_7d_ids": sin_rep_ids,
    }), 200


@api_bp.route('/casas_de_paz/<int:cdp_id>', methods=['GET'])
@api_auth_required
def api_get_cdp_detalle(cdp_id):
    """Retorna la ficha técnica y auditoría completa de una Casa de Paz."""
    usuario_id = session.get("usuario_id")
    rol = session.get("rol")

    cdp = get_cdp_detalle(cdp_id)
    if not cdp:
        if not mock_mode_enabled() and get_db_connection() is None:
            return _db_unavailable_response()
        return jsonify({"error": "Casa de Paz no encontrada"}), 404

    if rol == 'supervisor':
        sup_red = get_supervisor_red_id(usuario_id)
        user_ctx = UserContext(usuario_id=str(usuario_id), rol=rol, supervisor_red_id=sup_red)
        if not AccessPolicy.can_access_cdp(user_ctx, cdp_id, cdp_red_id=cdp.get('red_id')):
            return jsonify({"error": "No autorizado para consultar esta Casa de Paz"}), 403
    elif rol in ('lider_cdp', 'cdp'):
        cdp_propia, _ = get_cdp_datos_usuario(usuario_id)
        own_cdp_id = cdp_propia['id'] if cdp_propia else None
        user_ctx = UserContext(usuario_id=str(usuario_id), rol=rol, cdp_id=own_cdp_id)
        if not AccessPolicy.can_access_cdp(user_ctx, cdp_id, cdp_red_id=cdp.get('red_id')):
            return jsonify({"error": "No autorizado para consultar esta Casa de Paz"}), 403
    elif rol != 'admin':
        return jsonify({"error": "No autorizado para consultar esta Casa de Paz"}), 403

    return jsonify({"cdp": _serialize_item(cdp)}), 200


@api_bp.route('/casas_de_paz', methods=['POST'])
@api_role_required('admin')
def api_crear_cdp():
    """Creación de una nueva Casa de Paz."""
    raw_data = request.get_json(silent=True) or request.form.to_dict() or {}
    dto = parse_payload(CdpCreateDTO, raw_data)
    ok, mensaje = crear_cdp_servicio(dto.to_service_dict())
    if ok:
        return jsonify({"success": True, "message": mensaje}), 201
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/casas_de_paz/<int:cdp_id>', methods=['PUT', 'POST'])
@api_role_required('admin')
def api_editar_cdp(cdp_id):
    """Edición de datos de una Casa de Paz existente."""
    raw_data = request.get_json(silent=True) or request.form.to_dict() or {}
    dto = parse_payload(CdpUpdateDTO, raw_data)
    ok, mensaje = actualizar_cdp_servicio(cdp_id, dto.to_service_dict())
    if ok:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/casas_de_paz/<int:cdp_id>/toggle', methods=['POST'])
@api_role_required('admin')
def api_toggle_cdp(cdp_id):
    """Alterna estado activa/pausada de una Casa de Paz."""
    ok, status, mensaje = toggle_cdp_servicio(cdp_id)
    if ok:
        return jsonify({"success": True, "status": status, "message": mensaje}), 200
    return jsonify({"success": False, "status": status, "error": mensaje}), 400


@api_bp.route('/casas_de_paz/<int:cdp_id>', methods=['DELETE'])
@api_role_required('admin')
def api_eliminar_cdp(cdp_id):
    """Baja defensiva de una Casa de Paz."""
    ok, categoria, mensaje = eliminar_cdp_servicio(cdp_id)
    if ok:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/lideres', methods=['GET'])
@api_auth_required
def api_get_lideres():
    """Directorio de líderes ministeriales paginado y filtrado."""
    usuario_id = session.get("usuario_id")
    rol = session.get("rol")

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
            return jsonify({"lideres": [], "total": 0, "page": page, "pages": 1, "per_page": per_page}), 200
        user_ctx = UserContext(usuario_id=str(usuario_id), rol=rol, supervisor_red_id=sup_red)
        if red_id_arg and not AccessPolicy.can_access_red(user_ctx, red_id_arg):
            return jsonify({"error": "No autorizado para consultar líderes fuera de su red asignada"}), 403
        supervisor_red_id = sup_red
        target_red_id = str(sup_red)
    elif rol in ('lider_cdp', 'cdp'):
        cdp_propia, _ = get_cdp_datos_usuario(usuario_id)
        if not cdp_propia:
            return jsonify({"lideres": [], "total": 0, "page": page, "pages": 1, "per_page": per_page}), 200
        own_cdp_id = str(cdp_propia['id'])
        own_red_id = cdp_propia.get('red_id')
        if red_id_arg and own_red_id is not None and str(red_id_arg) != str(own_red_id):
            return jsonify({"error": "No autorizado para consultar líderes de otra red"}), 403
        if cdp_id_arg and str(cdp_id_arg) != own_cdp_id:
            return jsonify({"error": "No autorizado para consultar líderes de otra Casa de Paz"}), 403
        cdp_id_arg = own_cdp_id
        target_red_id = ''

    repo = get_lider_repository()
    if isinstance(repo, NullLiderRepository):
        return _db_unavailable_response()
    lideres, total, _, _ = repo.list_lideres(
        search=search,
        rol=rol_filtro,
        red_id=target_red_id,
        cdp_id=cdp_id_arg,
        supervisor_red_id=supervisor_red_id,
        page=page,
        per_page=per_page,
    )
    total_pages = max((total + per_page - 1) // per_page, 1) if total else 1
    return jsonify({
        "lideres": _serialize_item(lideres),
        "total": total,
        "page": page,
        "pages": total_pages,
        "per_page": per_page,
    }), 200


@api_bp.route('/lideres/<int:lider_id>', methods=['GET'])
@api_role_required('admin', 'supervisor')
def api_get_lider_detalle(lider_id):
    """Consulta de datos de un líder específico para edición."""
    usuario_id = session.get("usuario_id")
    rol = session.get("rol")

    lider = obtener_lider_servicio(lider_id)
    if not lider:
        return jsonify({"error": "Líder no encontrado"}), 404

    if rol == 'supervisor':
        sup_red = get_supervisor_red_id(usuario_id)
        lider_red_id = lider.get('red_id')
        if lider_red_id is None and lider.get('cdp_id'):
            cdp_info = get_cdp_detalle(lider['cdp_id'])
            lider_red_id = cdp_info.get('red_id') if cdp_info else None
        user_ctx = UserContext(usuario_id=str(usuario_id), rol=rol, supervisor_red_id=sup_red)
        if not AccessPolicy.can_access_cdp(user_ctx, lider.get('cdp_id'), cdp_red_id=lider_red_id):
            return jsonify({"error": "No autorizado para consultar este líder"}), 403

    return jsonify({"lider": _serialize_item(lider)}), 200


@api_bp.route('/lideres', methods=['POST'])
@api_role_required('admin')
def api_crear_lider():
    """Registro de un nuevo líder ministerial."""
    raw_data = request.get_json(silent=True) or request.form.to_dict() or {}
    dto = parse_payload(LiderCreateDTO, raw_data)
    ok, mensaje = crear_lider_servicio(dto.to_service_dict())
    if ok:
        return jsonify({"success": True, "message": mensaje}), 201
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/lideres/<int:lider_id>', methods=['PUT', 'POST'])
@api_role_required('admin')
def api_editar_lider(lider_id):
    """Actualización de un líder ministerial."""
    raw_data = request.get_json(silent=True) or request.form.to_dict() or {}
    dto = parse_payload(LiderUpdateDTO, raw_data)
    ok, mensaje = actualizar_lider_servicio(lider_id, dto.to_service_dict())
    if ok:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/lideres/<int:lider_id>/toggle', methods=['POST'])
@api_role_required('admin')
def api_toggle_lider(lider_id):
    """Alterna estado activo/pausado de un líder."""
    ok, status, mensaje = toggle_lider_servicio(lider_id)
    if ok:
        return jsonify({"success": True, "status": status, "message": mensaje}), 200
    return jsonify({"success": False, "status": status, "error": mensaje}), 400


@api_bp.route('/lideres/<int:lider_id>', methods=['DELETE'])
@api_role_required('admin')
def api_eliminar_lider(lider_id):
    """Eliminación defensiva de un líder con candado de historial."""
    ok, categoria, mensaje = eliminar_lider_servicio(lider_id)
    if ok:
        return jsonify({"success": True, "message": mensaje}), 200
    return jsonify({"success": False, "error": mensaje}), 400


@api_bp.route('/estructura/selectores', methods=['GET'])
@api_role_required('admin', 'supervisor')
def api_get_estructura_selectores():
    """Retorna opciones para los selectores de formularios de redes y casas."""
    usuario_id = session.get("usuario_id")
    rol = session.get("rol")
    cdp_id = request.args.get('cdp_id', type=int)

    if rol == 'supervisor':
        sup_red = get_supervisor_red_id(usuario_id)
        if not sup_red:
            return jsonify({
                "supervisores": [],
                "lideres_cdp": [],
                "casas_de_paz": [],
                "redes": [],
            }), 200
        cdps_all = obtener_cdps_para_select() or []
        cdps = [c for c in cdps_all if str(c.get('red_id', '')) == str(sup_red)]
        repo = get_estructura_repository()
        if isinstance(repo, NullEstructuraRepository):
            return _db_unavailable_response()
        redes = repo.list_redes(supervisor_red_id=sup_red) or []
        return jsonify({
            "supervisores": [],
            "lideres_cdp": [],
            "casas_de_paz": _serialize_item(cdps),
            "redes": _serialize_item(redes),
        }), 200

    supervisores = get_supervisores_disponibles_servicio()
    lideres_cdp = get_lideres_cdp_disponibles_servicio(cdp_id=cdp_id)
    cdps = obtener_cdps_para_select()

    repo = get_estructura_repository()
    redes = repo.list_all_redes_select()

    return jsonify({
        "supervisores": _serialize_item(supervisores or []),
        "lideres_cdp": _serialize_item(lideres_cdp or []),
        "casas_de_paz": _serialize_item(cdps or []),
        "redes": _serialize_item(redes or [])
    }), 200
